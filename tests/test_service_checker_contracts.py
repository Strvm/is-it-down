from collections.abc import Sequence
from math import isclose

from is_it_down.checkers.base import BaseCheck, BaseServiceChecker
from is_it_down.scripts.run_service_checker import discover_service_checkers


def test_all_service_checkers_follow_base_contracts() -> None:
    discovered = discover_service_checkers()
    assert discovered

    for service_key, checker_cls in discovered.items():
        checker = checker_cls()
        assert isinstance(checker, BaseServiceChecker)
        assert isinstance(checker.service_key, str)
        assert checker.service_key
        assert checker.service_key == service_key

        assert isinstance(checker.dependencies, Sequence)
        dependency_keys = checker.dependency_service_keys()
        assert checker.service_key not in dependency_keys
        assert len(dependency_keys) == len(checker.dependencies)
        for dependency in checker.dependencies:
            assert isinstance(dependency, type)
            assert issubclass(dependency, BaseServiceChecker)

        if checker.official_uptime is not None:
            assert checker.official_uptime.startswith("http://") or checker.official_uptime.startswith(
                "https://"
            )


def test_all_service_checkers_expose_valid_check_definitions() -> None:
    discovered = discover_service_checkers()
    assert discovered

    for checker_cls in discovered.values():
        checker = checker_cls()
        checks = list(checker.build_checks())

        assert checks
        assert len({check.check_key for check in checks}) == len(checks)

        for check in checks:
            assert isinstance(check, BaseCheck)
            assert isinstance(check.check_key, str) and check.check_key
            assert isinstance(check.endpoint_key, str) and check.endpoint_key
            assert check.interval_seconds > 0
            assert check.timeout_seconds > 0
            if check.weight is not None:
                assert check.weight > 0
                assert check.weight <= 1


def test_all_service_checkers_resolve_weights_to_one() -> None:
    discovered = discover_service_checkers()
    assert discovered

    for checker_cls in discovered.values():
        checker = checker_cls()
        resolved = checker.resolve_check_weights(list(checker.build_checks()))
        assert resolved
        assert isclose(sum(check.weight or 0.0 for check in resolved), 1.0, rel_tol=1e-9, abs_tol=1e-9)


def test_at_least_one_service_checker_has_three_or_more_checks() -> None:
    discovered = discover_service_checkers()
    assert discovered

    check_counts = [len(list(checker_cls().build_checks())) for checker_cls in discovered.values()]
    assert any(count >= 3 for count in check_counts)
