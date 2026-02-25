"""Provide functionality for `is_it_down.scripts.pr_checker_report`."""

import argparse
import asyncio
import importlib
import inspect
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

import httpx
from pydantic import BaseModel

from is_it_down.checkers.base import BaseServiceChecker
from is_it_down.scripts.checker_runtime import service_checker_path
from is_it_down.settings import get_settings

COMMENT_MARKER = "<!-- is-it-down-checker-results -->"
SERVICE_CHECKER_FILE_RE = re.compile(r"^src/is_it_down/checkers/services/(?P<module>[a-zA-Z0-9_]+)\.py$")


class CheckerExecutionResult(BaseModel):
    """Represent `CheckerExecutionResult`."""

    service_key: str
    checker_class: str
    official_uptime: str | None
    dependencies: list[str]
    changed_module: str
    checks: list[dict[str, Any]]
    error: str | None


def changed_service_checker_modules(changed_files: list[str]) -> list[str]:
    """Changed service checker modules.
    
    Args:
        changed_files: The changed files value.
    
    Returns:
        The resulting value.
    """
    modules: set[str] = set()
    for changed_file in changed_files:
        match = SERVICE_CHECKER_FILE_RE.match(changed_file)
        if match is None:
            continue
        module_name = match.group("module")
        if module_name == "__init__":
            continue
        modules.add(module_name)
    return sorted(modules)


def _dependency_service_keys_safe(checker: BaseServiceChecker) -> list[str]:
    """Dependency service keys safe.
    
    Args:
        checker: The checker value.
    
    Returns:
        The resulting value.
    """
    try:
        return checker.dependency_service_keys()
    except Exception:
        dependencies = getattr(checker, "dependencies", ())
        keys: list[str] = []
        for dependency in dependencies:
            dependency_key = getattr(dependency, "service_key", None)
            if isinstance(dependency_key, str) and dependency_key:
                keys.append(dependency_key)
            else:
                keys.append(str(dependency))
        return keys


def _service_module_path(module_name: str) -> str:
    """Service module path.
    
    Args:
        module_name: The module name value.
    
    Returns:
        The resulting value.
    """
    return f"is_it_down.checkers.services.{module_name}"


def _discover_service_checkers_for_module(
    module_name: str,
) -> tuple[list[type[BaseServiceChecker]], str | None]:
    """Discover service checkers for module.
    
    Args:
        module_name: The module name value.
    
    Returns:
        The resulting value.
    """
    module_path = _service_module_path(module_name)

    try:
        module = importlib.import_module(module_path)
    except Exception as exc:
        return [], f"{exc.__class__.__name__}: {exc}"

    discovered: list[type[BaseServiceChecker]] = []
    for _, loaded in inspect.getmembers(module, inspect.isclass):
        if not issubclass(loaded, BaseServiceChecker):
            continue
        if loaded is BaseServiceChecker:
            continue
        if loaded.__module__ != module_path:
            continue
        discovered.append(loaded)

    if not discovered:
        return [], "No BaseServiceChecker subclasses found in module."
    return discovered, None


def selected_service_checker_classes(
    changed_files: list[str],
) -> list[tuple[str, type[BaseServiceChecker]]]:
    """Selected service checker classes.
    
    Args:
        changed_files: The changed files value.
    
    Returns:
        The resulting value.
    """
    selected, _ = selected_service_checker_classes_with_errors(changed_files)
    return selected


def selected_service_checker_classes_with_errors(
    changed_files: list[str],
) -> tuple[list[tuple[str, type[BaseServiceChecker]]], dict[str, str]]:
    """Selected service checker classes with errors.
    
    Args:
        changed_files: The changed files value.
    
    Returns:
        The resulting value.
    """
    modules = changed_service_checker_modules(changed_files)

    selected: list[tuple[str, type[BaseServiceChecker]]] = []
    module_errors: dict[str, str] = {}
    for module_name in modules:
        checker_classes, module_error = _discover_service_checkers_for_module(module_name)
        if module_error is not None:
            module_errors[module_name] = module_error
            continue

        for checker_cls in sorted(checker_classes, key=lambda loaded: loaded.service_key):
            selected.append((module_name, checker_cls))
    return selected, module_errors


async def run_selected_service_checkers(
    selected: list[tuple[str, type[BaseServiceChecker]]],
) -> list[CheckerExecutionResult]:
    """Run selected service checkers.
    
    Args:
        selected: The selected value.
    
    Returns:
        The resulting value.
    """
    settings = get_settings()
    timeout = httpx.Timeout(settings.default_http_timeout_seconds)

    async with httpx.AsyncClient(
        timeout=timeout,
        headers={"User-Agent": settings.user_agent},
        follow_redirects=True,
    ) as client:
        results: list[CheckerExecutionResult] = []
        for changed_module, checker_cls in selected:
            checker = checker_cls()
            checker_path = service_checker_path(checker_cls)

            try:
                run_result = await checker.run_all(client)
                check_payloads = [
                    {
                        "check_key": check_result.check_key,
                        "status": check_result.status,
                        "observed_at": check_result.observed_at.isoformat(),
                        "latency_ms": check_result.latency_ms,
                        "http_status": check_result.http_status,
                        "error_code": check_result.error_code,
                        "error_message": check_result.error_message,
                        "metadata": check_result.metadata,
                    }
                    for check_result in run_result.check_results
                ]

                results.append(
                    CheckerExecutionResult(
                        service_key=run_result.service_key,
                        checker_class=checker_path,
                        official_uptime=checker.official_uptime,
                        dependencies=_dependency_service_keys_safe(checker),
                        changed_module=changed_module,
                        checks=check_payloads,
                        error=None,
                    )
                )
            except Exception as exc:
                results.append(
                    CheckerExecutionResult(
                        service_key=getattr(checker, "service_key", checker_cls.__name__),
                        checker_class=checker_path,
                        official_uptime=getattr(checker, "official_uptime", None),
                        dependencies=_dependency_service_keys_safe(checker),
                        changed_module=changed_module,
                        checks=[],
                        error=str(exc),
                    )
                )

        return results


def _status_summary(run_result: CheckerExecutionResult) -> str:
    """Status summary.
    
    Args:
        run_result: The run result value.
    
    Returns:
        The resulting value.
    """
    counts = {"up": 0, "degraded": 0, "down": 0}
    for check in run_result.checks:
        status = check.get("status")
        if status in counts:
            counts[status] += 1

    total = len(run_result.checks)
    return f"{counts['up']} up / {counts['degraded']} degraded / {counts['down']} down ({total} checks)"


def render_comment_markdown(
    *,
    changed_files: list[str],
    selected_modules: list[str],
    results: list[CheckerExecutionResult],
    verbose: bool = False,
    module_errors: Mapping[str, str] | None = None,
) -> str:
    """Render comment markdown.
    
    Args:
        changed_files: The changed files value.
        selected_modules: The selected modules value.
        results: The results value.
        verbose: The verbose value.
        module_errors: The module errors value.
    
    Returns:
        The resulting value.
    """
    lines: list[str] = [COMMENT_MARKER, "## Service Checker Preview"]

    generated_at = datetime.now(UTC).isoformat()
    lines.append(f"Generated at `{generated_at}`.")

    if not selected_modules:
        lines.append("")
        lines.append("No added/modified service checker files were detected in this PR.")
        return "\n".join(lines)

    lines.append("")
    lines.append("Changed service checker modules:")
    for module_name in selected_modules:
        lines.append(f"- `{module_name}`")

    if module_errors:
        lines.append("")
        lines.append("Module import/discovery issues:")
        for module_name in sorted(module_errors):
            lines.append(f"- `{module_name}`: `{module_errors[module_name]}`")

    lines.append("")
    lines.append("| Service | Checker | Dependencies | Result |")
    lines.append("|---|---|---|---|")

    for result in results:
        dependencies = ", ".join(result.dependencies) if result.dependencies else "-"
        summary = "error" if result.error else _status_summary(result)
        lines.append(f"| `{result.service_key}` | `{result.checker_class}` | `{dependencies}` | {summary} |")

    lines.append("")
    lines.append("Full JSON payload is uploaded as the workflow artifact `checker-preview-results`.")
    lines.append("")
    for result in results:
        lines.append(f"<details><summary><strong>{result.service_key}</strong> ({result.changed_module})</summary>")
        lines.append("")

        if result.official_uptime:
            lines.append(f"Official uptime: {result.official_uptime}")
            lines.append("")

        if result.error:
            lines.append(f"Execution error: `{result.error}`")
            lines.append("")
            lines.append("</details>")
            lines.append("")
            continue

        lines.append("| Check | Status | HTTP | Latency | Error |")
        lines.append("|---|---|---|---|---|")
        for check in result.checks:
            error_parts = [part for part in [check.get("error_code"), check.get("error_message")] if part]
            error_text = " / ".join(error_parts) if error_parts else "-"
            http_status = check.get("http_status") if check.get("http_status") is not None else "-"
            latency = check.get("latency_ms")
            latency_text = f"{latency}ms" if latency is not None else "-"

            lines.append(
                f"| `{check.get('check_key', '-')}` | `{check.get('status', '-')}` | "
                f"`{http_status}` | `{latency_text}` | {error_text} |"
            )

        if verbose:
            non_up_checks = [check for check in result.checks if check.get("status") in {"degraded", "down"}]
            if non_up_checks:
                lines.append("")
                lines.append(f"<details><summary>Verbose non-up check logs ({len(non_up_checks)})</summary>")
                lines.append("")
                for check in non_up_checks:
                    lines.append(f"Check: `{check.get('check_key', '-')}`")
                    lines.append("```json")
                    lines.append(json.dumps(check, indent=2, sort_keys=True))
                    lines.append("```")
                    lines.append("")
                lines.append("</details>")

        lines.append("")
        lines.append("</details>")
        lines.append("")

    lines.append("Changed files considered:")
    for changed_file in changed_files:
        lines.append(f"- `{changed_file}`")

    return "\n".join(lines)


def _parse_args() -> argparse.Namespace:
    """Parse args.
    
    Returns:
        The resulting value.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Run added/modified service checkers for a PR and render a markdown comment body with checker results."
        )
    )
    parser.add_argument("--changed-files-json", required=True, help="JSON list of changed files")
    parser.add_argument("--output-markdown", required=True, help="Output markdown file path")
    parser.add_argument("--output-json", required=True, help="Output JSON file path")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Include verbose non-up check payloads in the generated markdown comment.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the entrypoint.
    
    Raises:
        ValueError: If an error occurs while executing this function.
    """
    args = _parse_args()
    changed_files = json.loads(args.changed_files_json)
    if not isinstance(changed_files, list) or not all(isinstance(item, str) for item in changed_files):
        raise ValueError("--changed-files-json must decode into a list of strings.")

    changed_modules = changed_service_checker_modules(changed_files)
    selected, module_errors = selected_service_checker_classes_with_errors(changed_files)
    selected_modules = changed_modules

    results: list[CheckerExecutionResult] = []
    if selected:
        results = asyncio.run(run_selected_service_checkers(selected))

    for module_name, module_error in sorted(module_errors.items()):
        results.append(
            CheckerExecutionResult(
                service_key=module_name,
                checker_class=_service_module_path(module_name),
                official_uptime=None,
                dependencies=[],
                changed_module=module_name,
                checks=[],
                error=module_error,
            )
        )

    markdown = render_comment_markdown(
        changed_files=changed_files,
        selected_modules=selected_modules,
        results=results,
        verbose=args.verbose,
        module_errors=module_errors,
    )

    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "changed_files": changed_files,
        "changed_modules": changed_modules,
        "selected_modules": selected_modules,
        "module_errors": module_errors,
        "verbose": args.verbose,
        "results": [result.model_dump() for result in results],
    }

    Path(args.output_markdown).write_text(markdown, encoding="utf-8")
    Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
