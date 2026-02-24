# is-it-down

`is-it-down` is an open-source, backend-first service health platform inspired by outage trackers, but driven by direct API checks instead of crowdsourced reports.

## Goals

- Run async endpoint checks for many services at high cadence.
- Compute weighted service health scores from multiple endpoint probes.
- Model service dependencies and attribute probable root causes.
- Expose current status + history through FastAPI REST and SSE.

## Core Services

- `api`: FastAPI status API and SSE stream.
- `scheduler`: Enqueues due checks.
- `worker`: Executes checks asynchronously and writes results.

## Local Development

```bash
uv sync --extra dev
uv run alembic upgrade head
uv run is-it-down-seed-demo
uv run is-it-down-api
uv run is-it-down-scheduler
uv run is-it-down-worker
```

## Run Service Checkers Without DB Writes

Use the local runner to execute service checkers directly in terminal (for testing/debugging only):

```bash
# list available service checker keys
uv run is-it-down-run-service-checker --list

# run by service key
uv run is-it-down-run-service-checker cloudflare

# run by class path and return JSON
uv run is-it-down-run-service-checker is_it_down.checkers.services.cloudflare.CloudflareServiceChecker --json

# fail non-zero if any check is degraded/down
uv run is-it-down-run-service-checker cloudflare --strict
```

Set environment variables:

- `IS_IT_DOWN_DATABASE_URL`: PostgreSQL DSN.
- `IS_IT_DOWN_ENV`: `local`, `staging`, or `production`.

## Project Layout

- `src/is_it_down/api`: FastAPI application.
- `src/is_it_down/checkers`: OOP async checker framework + service checks.
- `src/is_it_down/scheduler`: due check scheduler.
- `src/is_it_down/worker`: async check executor.
- `src/is_it_down/db`: SQLAlchemy models and session management.
- `infra/terraform`: Cloud Run + Cloud SQL baseline infra.
- `.github/workflows`: CI and deploy workflows.
