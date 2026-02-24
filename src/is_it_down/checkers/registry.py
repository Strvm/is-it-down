import importlib
import inspect
import pkgutil
from collections.abc import Iterator

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker


class CheckerRegistry:
    def __init__(self) -> None:
        self._check_cache: dict[str, type[BaseCheck]] = {}
        self._service_cache: dict[str, type[BaseServiceChecker]] = {}

    def register(self, path: str, check_cls: type[BaseCheck]) -> None:
        self._check_cache[path] = check_cls

    def get(self, path: str) -> type[BaseCheck]:
        return self.get_check(path)

    def get_check(self, path: str) -> type[BaseCheck]:
        if path not in self._check_cache:
            self._check_cache[path] = self._load_check_class(path)
        return self._check_cache[path]

    def get_service_checker(self, path: str) -> type[BaseServiceChecker]:
        if path not in self._service_cache:
            self._service_cache[path] = self._load_service_checker_class(path)
        return self._service_cache[path]

    def discover_under(self, package_name: str) -> Iterator[str]:
        package = importlib.import_module(package_name)
        for module_info in pkgutil.walk_packages(package.__path__, prefix=f"{package_name}."):
            importlib.import_module(module_info.name)
            yield module_info.name

    def discover_service_checkers(
        self, package_name: str = "is_it_down.checkers.services"
    ) -> Iterator[type[BaseServiceChecker]]:
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
        module_name, class_name = path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        loaded = getattr(module, class_name)
        if not issubclass(loaded, BaseCheck):
            raise TypeError(f"{path} does not resolve to a BaseCheck subclass.")
        return loaded

    @staticmethod
    def _load_service_checker_class(path: str) -> type[BaseServiceChecker]:
        module_name, class_name = path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        loaded = getattr(module, class_name)
        if not issubclass(loaded, BaseServiceChecker):
            raise TypeError(f"{path} does not resolve to a BaseServiceChecker subclass.")
        return loaded


registry = CheckerRegistry()
