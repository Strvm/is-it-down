# is-it-down

`is-it-down` is an open-source service health platform that uses direct endpoint checks (not crowdsourced reports) to determine service status.

It is designed to be easy to extend: if you want to add a new service checker, improve reliability signals, or improve API/UI output, this repo is built for that workflow.

## Why Contribute

- Add support for more services.
- Improve checker quality (fewer false positives / false negatives).
- Improve status attribution for dependency-driven incidents.
- Improve the FastAPI backend and Next.js dashboard experience.

## Architecture At A Glance

```text
Service Checkers -> BigQuery -> FastAPI API -> Next.js Web App
```

Runtime components:

- `checker-job`: runs service checkers and writes check rows to BigQuery.
- `api`: FastAPI service that serves status and incident data.
- `web`: Next.js 16 app in `web/` that consumes the API.

## Quick Start (Backend)

Prerequisites:

- Python `3.13+`
- [`uv`](https://docs.astral.sh/uv/)

Install deps and run core validation:

```bash
uv sync --extra dev
uv run --extra dev ruff check .
uv run --extra dev pytest
```

List and run checkers locally (no BigQuery writes):

```bash
uv run is-it-down-run-service-checker --list
uv run is-it-down-run-service-checker cloudflare
uv run is-it-down-run-service-checker cloudflare --json
```

Run scheduled checks with BigQuery writes disabled:

```bash
uv run is-it-down-run-scheduled-checks --dry-run
```

Find BaseChecks that were `degraded`/`down` in the last 48 hours:

```bash
uv run find-failing-base-checkers
uv run find-failing-base-checkers --json
uv run find-failing-base-checkers --service-key cloudflare --lookback-hours 24
```

## Run API Locally

```bash
uv run is-it-down-api
```

Health endpoint:

```bash
curl http://localhost:8080/healthz
```

## Quick Start (Frontend)

Prerequisites:

- `bun` (project uses `bun@1.2.16`)

```bash
cd web
bun install
cp .env.example .env.local
bun dev
```

Frontend env vars:

- `API_BASE_URL`: server-side fetch base URL.
- `NEXT_PUBLIC_API_BASE_URL`: client-side API base URL.

## Common Contributor Workflows

### Add or Improve a Service Checker

1. Create/update checker module(s) in `src/is_it_down/checkers/services/`.
2. Keep checks focused and independent (status page + API + web edge checks is a common pattern).
3. Make sure non-up results include debug metadata.
4. Validate with:

```bash
uv run --extra dev ruff check .
uv run --extra dev pytest
uv run is-it-down-run-service-checker --list
uv run is-it-down-run-service-checker <service_key> --json
uv run is-it-down-run-service-checker <service_key> --verbose
```

### Backend Changes (API / Core / Worker)

Use this pre-PR pass:

```bash
uv run --extra dev ruff check .
uv run --extra dev pytest
```

### Frontend Changes

```bash
cd web
bun run lint
bun run build
```

## Environment Variables

Most local contributor workflows only need defaults, but these are commonly used:

- `IS_IT_DOWN_ENV`: `local`, `development`, or `production`.
- `IS_IT_DOWN_DEFAULT_CHECKER_PROXY_URL`: local proxy override for checks that use `proxy_setting="default"`.
- `IS_IT_DOWN_PROXY_SECRET_PROJECT_ID`: GCP project containing checker proxy secrets.
- `IS_IT_DOWN_DEFAULT_CHECKER_PROXY_SECRET_ID`: default proxy secret ID.

BigQuery settings (for non-dry-run scheduled checks / API integrations):

- `IS_IT_DOWN_BIGQUERY_PROJECT_ID`
- `IS_IT_DOWN_BIGQUERY_DATASET_ID` (default: `is_it_down`)
- `IS_IT_DOWN_BIGQUERY_TABLE_ID` (default: `check_results`)
- `IS_IT_DOWN_TRACKING_BIGQUERY_DATASET_ID` (default: `is_it_down_tracking`)
- `IS_IT_DOWN_TRACKING_BIGQUERY_TABLE_ID` (default: `service_detail_views`)

API cache + Redis settings:

- `IS_IT_DOWN_API_CACHE_ENABLED` (default: `true`)
- `IS_IT_DOWN_API_CACHE_TTL_SECONDS` (default: `60`)
- `IS_IT_DOWN_API_CACHE_KEY_PREFIX` (default: `is-it-down:api:v1`)
- `IS_IT_DOWN_API_CACHE_REDIS_URL` (optional direct Redis URL; useful for local development)
- `IS_IT_DOWN_API_CACHE_REDIS_SECRET_ID` (Secret Manager secret ID/resource for Redis URL)
- `IS_IT_DOWN_REDIS_SECRET_PROJECT_ID` (project used when secret ID is short and not fully-qualified)
- `IS_IT_DOWN_API_CACHE_WARM_ON_CHECKER_JOB` (default: `true`)
- `IS_IT_DOWN_API_CACHE_WARM_IMPACTED_SERVICE_LIMIT` (default: `25`)

## Project Layout

- `src/is_it_down/checkers`: checker framework, utilities, and service checkers.
- `src/is_it_down/api`: FastAPI routes and API infrastructure.
- `src/is_it_down/core`: scoring, attribution, and shared domain models.
- `src/is_it_down/scripts/run_service_checker.py`: local ad-hoc checker runner.
- `src/is_it_down/scripts/run_scheduled_checks.py`: checker job entrypoint.
- `web/`: Next.js dashboard.
- `infra/terraform`: Cloud Run + Cloud Scheduler + BigQuery infra.

## CI and Deployment

CI (`.github/workflows/ci.yml`) runs:

- `ruff check src tests`
- `pytest -q`

Deployment summary:

- Push to `main` deploys `dev` (`is-it-down-dev`).
- GitHub Release deploys `prod` (`is-it-down-prod`).
- Images built/pushed: `checker`, `api`, `web`.
- Terraform applies the image tag to Cloud Run resources.

Required GitHub secret for deploy workflows:

- `GCP_SA_KEY` (configured per GitHub Environment, e.g. `dev` and `prod`).

## Contributing Expectations

- Prefer small, focused PRs.
- Include tests when behavior changes.
- Keep checker logic defensive against partial/malformed payloads.
- Run lint + tests before opening a PR.
- If adding a new checker, include enough metadata/debug info to make production triage easy.

If you are new to the codebase, a great first contribution is improving one service checker's signal quality and adding regression tests for that behavior.
