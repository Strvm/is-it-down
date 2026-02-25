"""Provide functionality for `is_it_down.checkers.registry`."""

import importlib
import inspect
import pkgutil
from collections.abc import Iterator

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker


class CheckerRegistry:
    """Represent `CheckerRegistry`."""

    def __init__(self) -> None:
        """Initialize the instance."""
        self._check_cache: dict[str, type[BaseCheck]] = {}
        self._service_cache: dict[str, type[BaseServiceChecker]] = {}

    def register(self, path: str, check_cls: type[BaseCheck]) -> None:
        """Register.
        
        Args:
            path: The path value.
            check_cls: The check cls value.
        """
        self._check_cache[path] = check_cls

    def get(self, path: str) -> type[BaseCheck]:
        """Get.
        
        Args:
            path: The path value.
        
        Returns:
            The resulting value.
        """
        return self.get_check(path)

    def get_check(self, path: str) -> type[BaseCheck]:
        """Get check.
        
        Args:
            path: The path value.
        
        Returns:
            The resulting value.
        """
        if path not in self._check_cache:
            self._check_cache[path] = self._load_check_class(path)
        return self._check_cache[path]

    def get_service_checker(self, path: str) -> type[BaseServiceChecker]:
        """Get service checker.
        
        Args:
            path: The path value.
        
        Returns:
            The resulting value.
        """
        if path not in self._service_cache:
            self._service_cache[path] = self._load_service_checker_class(path)
        return self._service_cache[path]

    def discover_under(self, package_name: str) -> Iterator[str]:
        """Discover under.
        
        Args:
            package_name: The package name value.
        
        Yields:
            The values produced by the generator.
        """
        package = importlib.import_module(package_name)
        for module_info in pkgutil.walk_packages(package.__path__, prefix=f"{package_name}."):
            importlib.import_module(module_info.name)
            yield module_info.name

    def discover_service_checkers(
        self, package_name: str = "is_it_down.checkers.services"
    ) -> Iterator[type[BaseServiceChecker]]:
        """Discover service checkers.
        
        Args:
            package_name: The package name value.
        
        Yields:
            The values produced by the generator.
        """
        for module_name in self.discover_under(package_name):
            module = importlib.import_module(module_name)
            for _, loaded in inspect.getmembers(module, inspect.isclass):
                if not issubclass(loaded, BaseServiceChecker):
                    continue
                if loaded is BaseServiceChecker:
                    continue
                if loaded.__module__ != module_name:
                    continue
                yield loaded

    @staticmethod
    def _load_check_class(path: str) -> type[BaseCheck]:
        """Load check class.
        
        Args:
            path: The path value.
        
        Returns:
            The resulting value.
        
        Raises:
            TypeError: If an error occurs while executing this function.
        """
        module_name, class_name = path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        loaded = getattr(module, class_name)
        if not issubclass(loaded, BaseCheck):
            raise TypeError(f"{path} does not resolve to a BaseCheck subclass.")
        return loaded

    @staticmethod
    def _load_service_checker_class(path: str) -> type[BaseServiceChecker]:
        """Load service checker class.
        
        Args:
            path: The path value.
        
        Returns:
            The resulting value.
        
        Raises:
            TypeError: If an error occurs while executing this function.
        """
        module_name, class_name = path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        loaded = getattr(module, class_name)
        if not issubclass(loaded, BaseServiceChecker):
            raise TypeError(f"{path} does not resolve to a BaseServiceChecker subclass.")
        return loaded


registry = CheckerRegistry()
