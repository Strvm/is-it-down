import argparse
import asyncio
import json
import os
from collections.abc import Sequence
from typing import Any

import httpx

from is_it_down.checkers.base import BaseServiceChecker, ServiceRunResult
from is_it_down.checkers.proxy import clear_proxy_resolution_cache
from is_it_down.checkers.registry import registry
from is_it_down.settings import get_settings


def _service_checker_path(service_checker_cls: type[BaseServiceChecker]) -> str:
    return f"{service_checker_cls.__module__}.{service_checker_cls.__name__}"


def discover_service_checkers() -> dict[str, type[BaseServiceChecker]]:
    discovered: dict[str, type[BaseServiceChecker]] = {}
    for loaded in registry.discover_service_checkers():
        service_key = getattr(loaded, "service_key", None)
        if not isinstance(service_key, str):
            continue
        if not service_key:
            continue
        discovered[service_key] = loaded
    return discovered


def resolve_service_checker_targets(targets: Sequence[str]) -> list[type[BaseServiceChecker]]:
    if not targets:
        raise ValueError("At least one service checker target must be provided.")

    discovered = discover_service_checkers()
    resolved: list[type[BaseServiceChecker]] = []
    seen_paths: set[str] = set()

    for target in targets:
        if "." in target:
            loaded = registry.get_service_checker(target)
        else:
            loaded = discovered.get(target)
            if loaded is None:
                available = ", ".join(sorted(discovered)) or "none"
                raise ValueError(f"Unknown service checker key '{target}'. Available keys: {available}.")

        loaded_path = _service_checker_path(loaded)
        if loaded_path in seen_paths:
            continue

        resolved.append(loaded)
        seen_paths.add(loaded_path)

    return resolved


async def execute_service_checkers(
    service_checker_classes: Sequence[type[BaseServiceChecker]],
) -> list[tuple[type[BaseServiceChecker], ServiceRunResult]]:
    settings = get_settings()
    client_timeout = httpx.Timeout(settings.default_http_timeout_seconds)

    async with httpx.AsyncClient(
        timeout=client_timeout,
        headers={"User-Agent": settings.user_agent},
        follow_redirects=True,
    ) as client:
        return [
            (service_checker_cls, await service_checker_cls().run_all(client))
            for service_checker_cls in service_checker_classes
        ]


def _check_result_payload(check_result: Any) -> dict[str, Any]:
    return {
        "check_key": check_result.check_key,
        "status": check_result.status,
        "observed_at": check_result.observed_at.isoformat(),
        "latency_ms": check_result.latency_ms,
        "http_status": check_result.http_status,
        "error_code": check_result.error_code,
        "error_message": check_result.error_message,
        "metadata": check_result.metadata,
    }


def _serialize_run(
    service_checker_cls: type[BaseServiceChecker],
    run_result: ServiceRunResult,
) -> dict[str, Any]:
    return {
        "service_key": run_result.service_key,
        "checker_class": _service_checker_path(service_checker_cls),
        "checks": [_check_result_payload(check_result) for check_result in run_result.check_results],
    }


def _print_human(
    service_checker_cls: type[BaseServiceChecker],
    run_result: ServiceRunResult,
    *,
    verbose: bool,
) -> None:
    print(f"Service: {run_result.service_key} ({_service_checker_path(service_checker_cls)})")
    if not run_result.check_results:
        print("  (no checks configured)\n")
        return

    header = f"{'CHECK':40} {'STATUS':9} {'LATENCY':9} {'HTTP':6} ERROR"
    print(header)
    print("-" * len(header))
    for check_result in run_result.check_results:
        latency = f"{check_result.latency_ms}ms" if check_result.latency_ms is not None else "-"
        http_status = str(check_result.http_status) if check_result.http_status is not None else "-"

        error = "-"
        if check_result.error_code or check_result.error_message:
            error = ": ".join(
                part for part in [check_result.error_code, check_result.error_message] if part is not None
            )

        print(f"{check_result.check_key[:40]:40} {check_result.status:9} {latency:9} {http_status:6} {error}")

        if check_result.metadata:
            metadata = json.dumps(check_result.metadata, sort_keys=True)
            print(f"{'':40} {'':9} {'':9} {'':6} metadata={metadata}")

        if verbose and check_result.status != "up":
            payload = json.dumps(_check_result_payload(check_result), indent=2, sort_keys=True)
            print(f"{'':40} {'':9} {'':9} {'':6} verbose:")
            for line in payload.splitlines():
                print(f"{'':40} {'':9} {'':9} {'':6} {line}")

    print("")


def _has_non_up_result(run_result: ServiceRunResult) -> bool:
    return any(check_result.status != "up" for check_result in run_result.check_results)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="is-it-down-run-service-checker",
        description="Run service checkers locally and print results without writing to the database.",
    )
    parser.add_argument(
        "targets",
        nargs="*",
        help=(
            "Service checker key (for example 'cloudflare') or full class path "
            "(for example 'is_it_down.checkers.services.cloudflare.CloudflareServiceChecker')."
        ),
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List discovered service checker keys and class paths.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print checker output as JSON.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any check result is not 'up'.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help=("Print detailed payload logs for non-up checks, including status code and response debug metadata."),
    )
    parser.add_argument(
        "--default-proxy-url",
        default=None,
        help=(
            "Optional direct proxy URL used when checks set proxy_setting='default'. "
            "Useful for local runs without Secret Manager access."
        ),
    )
    return parser


def _print_discovered_checkers() -> None:
    discovered = discover_service_checkers()
    if not discovered:
        print("No service checkers discovered.")
        return

    print("Discovered service checkers:")
    for service_key in sorted(discovered):
        print(f"- {service_key}: {_service_checker_path(discovered[service_key])}")


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.default_proxy_url is not None:
        os.environ["IS_IT_DOWN_DEFAULT_CHECKER_PROXY_URL"] = args.default_proxy_url
        get_settings.cache_clear()
        clear_proxy_resolution_cache()

    if args.list:
        _print_discovered_checkers()
        if not args.targets:
            return

    if not args.targets:
        parser.error("Provide at least one checker target or pass --list.")

    try:
        service_checker_classes = resolve_service_checker_targets(args.targets)
    except ValueError as exc:
        parser.error(str(exc))

    runs = asyncio.run(execute_service_checkers(service_checker_classes))

    if args.json:
        print(
            json.dumps(
                [_serialize_run(service_checker_cls, run_result) for service_checker_cls, run_result in runs],
                indent=2,
                sort_keys=True,
            )
        )
    else:
        for service_checker_cls, run_result in runs:
            _print_human(service_checker_cls, run_result, verbose=args.verbose)

    if args.strict and any(_has_non_up_result(run_result) for _, run_result in runs):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
