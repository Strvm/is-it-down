---
name: create-base-service-checker
description: Create or update service health checkers for this is-it-down repository. Use when adding a new BaseServiceChecker, adding or modifying BaseCheck endpoint probes, setting class-based service dependencies, configuring optional check weights that normalize to 1, wiring degraded/down debug metadata, and validating checker behavior locally and in PR checker-preview comments.
---

# Create BaseServiceChecker

Create new service checker modules that match this repository's checker architecture and quality bar.

## Implement Checker Module

1. Create `src/is_it_down/checkers/services/<service_name>.py`.
2. Define one `BaseServiceChecker` subclass:
- Set `service_key`.
- Set `official_uptime` to the official status page URL when available.
- Set `dependencies` as `Sequence[type[BaseServiceChecker]]` using checker class references (not strings).
3. Define one or more `BaseCheck` subclasses:
- Set `check_key`, `endpoint_key`, `interval_seconds`, `timeout_seconds`.
- Set `weight` only when needed. Keep unspecified weights as `None`.

## Follow Weight Rules

Rely on `BaseServiceChecker.resolve_check_weights()` behavior in `src/is_it_down/checkers/base.py`:

1. Keep each explicit weight `> 0` and `<= 1`.
2. Keep explicit-weight sum `<= 1`.
3. Let unspecified weights auto-distribute so total resolved weight equals `1`.
4. If all checks specify weights, make them sum exactly to `1`.

## Use Shared Checker Utilities

Import and use helpers in `src/is_it_down/checkers/utils.py`:

1. `status_from_http(response)`
2. `response_latency_ms(response)`
3. `apply_statuspage_indicator(base_status, indicator)` for statuspage-style APIs
4. `add_non_up_debug_metadata(metadata=..., status=..., response=...)` to capture debug body/status previews for degraded/down checks

Use these utilities instead of redefining response or status helper functions.

## Build Robust Check Logic

1. Keep each check focused on one endpoint and one concern.
2. Parse response payloads defensively (`.get`, type checks).
3. Prefer public/read-only endpoints for baseline health checks.
4. When checks are degraded/down, ensure response debug metadata is available via `add_non_up_debug_metadata`.
5. Avoid circular checker imports when setting dependencies.

## Validate End-to-End

Run all commands before finishing:

```bash
uv run --extra dev ruff check .
uv run --extra dev pytest
uv run is-it-down-run-service-checker --list
uv run is-it-down-run-service-checker <service_key> --json
uv run is-it-down-run-service-checker <service_key> --verbose
```

If preparing PR preview behavior, also run:

```bash
uv run python src/is_it_down/scripts/pr_checker_report.py \
  --changed-files-json '["src/is_it_down/checkers/services/<service_name>.py"]' \
  --output-markdown /tmp/checker-preview.md \
  --output-json /tmp/checker-preview.json \
  --verbose
```

## References

Read `references/service-checker-patterns.md` for a skeleton, checklist, and common pitfalls.
