import argparse
import asyncio
import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from is_it_down.checkers.base import BaseServiceChecker
from is_it_down.scripts.run_service_checker import discover_service_checkers
from is_it_down.settings import get_settings

COMMENT_MARKER = "<!-- is-it-down-checker-results -->"
SERVICE_CHECKER_FILE_RE = re.compile(r"^src/is_it_down/checkers/services/(?P<module>[a-zA-Z0-9_]+)\.py$")


@dataclass(slots=True)
class CheckerExecutionResult:
    service_key: str
    checker_class: str
    official_uptime: str | None
    dependencies: list[str]
    changed_module: str
    checks: list[dict[str, Any]]
    error: str | None


def changed_service_checker_modules(changed_files: list[str]) -> list[str]:
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


def _service_checker_path(service_checker_cls: type[BaseServiceChecker]) -> str:
    return f"{service_checker_cls.__module__}.{service_checker_cls.__name__}"


def selected_service_checker_classes(
    changed_files: list[str],
) -> list[tuple[str, type[BaseServiceChecker]]]:
    discovered = discover_service_checkers()
    modules = changed_service_checker_modules(changed_files)

    module_to_checkers: dict[str, list[type[BaseServiceChecker]]] = {}
    for checker_cls in discovered.values():
        module_name = checker_cls.__module__.split(".")[-1]
        module_to_checkers.setdefault(module_name, []).append(checker_cls)

    selected: list[tuple[str, type[BaseServiceChecker]]] = []
    for module_name in modules:
        checker_classes = module_to_checkers.get(module_name)
        if checker_classes is None:
            continue
        for checker_cls in sorted(checker_classes, key=lambda loaded: loaded.service_key):
            selected.append((module_name, checker_cls))
    return selected


async def run_selected_service_checkers(
    selected: list[tuple[str, type[BaseServiceChecker]]],
) -> list[CheckerExecutionResult]:
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
            checker_path = _service_checker_path(checker_cls)

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
                        dependencies=list(checker.dependencies),
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
                        dependencies=list(getattr(checker, "dependencies", ())),
                        changed_module=changed_module,
                        checks=[],
                        error=str(exc),
                    )
                )

        return results


def _status_summary(run_result: CheckerExecutionResult) -> str:
    counts = {"up": 0, "degraded": 0, "down": 0}
    for check in run_result.checks:
        status = check.get("status")
        if status in counts:
            counts[status] += 1

    total = len(run_result.checks)
    return (
        f"{counts['up']} up / {counts['degraded']} degraded / "
        f"{counts['down']} down ({total} checks)"
    )


def render_comment_markdown(
    *,
    changed_files: list[str],
    selected_modules: list[str],
    results: list[CheckerExecutionResult],
) -> str:
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

    lines.append("")
    lines.append("| Service | Checker | Dependencies | Result |")
    lines.append("|---|---|---|---|")

    for result in results:
        dependencies = ", ".join(result.dependencies) if result.dependencies else "-"
        summary = "error" if result.error else _status_summary(result)
        lines.append(
            f"| `{result.service_key}` | `{result.checker_class}` | `{dependencies}` | {summary} |"
        )

    lines.append("")
    for result in results:
        lines.append(
            f"<details><summary><strong>{result.service_key}</strong> "
            f"({result.changed_module})</summary>"
        )
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

        lines.append("")
        lines.append("</details>")
        lines.append("")

    lines.append("Changed files considered:")
    for changed_file in changed_files:
        lines.append(f"- `{changed_file}`")

    return "\n".join(lines)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run added/modified service checkers for a PR and render a markdown comment body "
            "with checker results."
        )
    )
    parser.add_argument("--changed-files-json", required=True, help="JSON list of changed files")
    parser.add_argument("--output-markdown", required=True, help="Output markdown file path")
    parser.add_argument("--output-json", required=True, help="Output JSON file path")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    changed_files = json.loads(args.changed_files_json)
    if not isinstance(changed_files, list) or not all(isinstance(item, str) for item in changed_files):
        raise ValueError("--changed-files-json must decode into a list of strings.")

    selected = selected_service_checker_classes(changed_files)
    selected_modules = [module_name for module_name, _ in selected]

    results: list[CheckerExecutionResult] = []
    if selected:
        results = asyncio.run(run_selected_service_checkers(selected))

    markdown = render_comment_markdown(
        changed_files=changed_files,
        selected_modules=selected_modules,
        results=results,
    )

    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "changed_files": changed_files,
        "selected_modules": selected_modules,
        "results": [asdict(result) for result in results],
    }

    Path(args.output_markdown).write_text(markdown, encoding="utf-8")
    Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
