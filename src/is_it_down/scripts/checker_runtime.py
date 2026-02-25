"""Provide shared runtime helpers for executing service checker classes."""

import asyncio
from collections.abc import Sequence

import httpx

from is_it_down.checkers.base import BaseServiceChecker, ServiceRunResult
from is_it_down.checkers.registry import registry
from is_it_down.settings import get_settings


def service_checker_path(service_checker_cls: type[BaseServiceChecker]) -> str:
    """Service checker path.
    
    Args:
        service_checker_cls: The service checker cls value.
    
    Returns:
        The resulting value.
    """
    return f"{service_checker_cls.__module__}.{service_checker_cls.__name__}"


def discover_service_checkers() -> dict[str, type[BaseServiceChecker]]:
    """Discover service checkers.
    
    Returns:
        The resulting value.
    """
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
    """Resolve service checker targets.
    
    Args:
        targets: The targets value.
    
    Returns:
        The resulting value.
    
    Raises:
        ValueError: If an error occurs while executing this function.
    """
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

        loaded_path = service_checker_path(loaded)
        if loaded_path in seen_paths:
            continue

        resolved.append(loaded)
        seen_paths.add(loaded_path)

    return resolved


async def execute_service_checkers(
    service_checker_classes: Sequence[type[BaseServiceChecker]],
    *,
    concurrent: bool = False,
    concurrency_limit: int | None = None,
) -> list[tuple[type[BaseServiceChecker], ServiceRunResult]]:
    """Execute service checkers.
    
    Args:
        service_checker_classes: The service checker classes value.
        concurrent: The concurrent value.
        concurrency_limit: The concurrency limit value.
    
    Returns:
        The resulting value.
    """
    settings = get_settings()
    client_timeout = httpx.Timeout(settings.default_http_timeout_seconds)

    async with httpx.AsyncClient(
        timeout=client_timeout,
        headers={"User-Agent": settings.user_agent},
        follow_redirects=True,
    ) as client:
        if not concurrent:
            return [
                (service_checker_cls, await service_checker_cls().run_all(client))
                for service_checker_cls in service_checker_classes
            ]

        limit = concurrency_limit or settings.checker_concurrency
        semaphore = asyncio.Semaphore(limit)

        async def _run_one(
            service_checker_cls: type[BaseServiceChecker],
        ) -> tuple[type[BaseServiceChecker], ServiceRunResult]:
            """Run one.
            
            Args:
                service_checker_cls: The service checker cls value.
            
            Returns:
                The resulting value.
            """
            async with semaphore:
                return service_checker_cls, await service_checker_cls().run_all(client)

        return await asyncio.gather(*[_run_one(service_checker_cls) for service_checker_cls in service_checker_classes])
