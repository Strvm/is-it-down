# is-it-down

`is-it-down` is an open-source, backend-first service health platform inspired by outage trackers, but driven by direct API checks instead of crowdsourced reports.

## Goals

- Run async endpoint checks for many services at high cadence.
- Persist raw check outcomes for analysis.
- Keep deployment simple with Cloud Run Jobs + BigQuery.

## Runtime

- `checker-job`: runs service checkers on a schedule and writes rows to BigQuery.
- `api`: FastAPI service serving status data from BigQuery.
- `web`: Next.js 16 dashboard UI in `web/` consuming the FastAPI service.

## Local Development

```bash
uv sync --extra dev
uv run is-it-down-run-service-checker --list
uv run is-it-down-run-scheduled-checks --dry-run
```

## Frontend Development

```bash
cd web
bun install
cp .env.example .env.local
bun dev
```

The frontend reads from:

- `API_BASE_URL` (server-side fetches)
- `NEXT_PUBLIC_API_BASE_URL` (client visibility/debug)

## Run Service Checkers Without BigQuery Writes

```bash
# list available service checker keys
uv run is-it-down-run-service-checker --list

# run by service key
uv run is-it-down-run-service-checker cloudflare

# run by class path and return JSON
uv run is-it-down-run-service-checker is_it_down.checkers.services.cloudflare.CloudflareServiceChecker --json
```

## Run Scheduled Checks (BigQuery Sink)

```bash
uv run is-it-down-run-scheduled-checks
```

Optional:

```bash
# run only selected checkers and fail non-zero if any check is non-up
uv run is-it-down-run-scheduled-checks cloudflare github --strict

# execute checks but skip BigQuery insert
uv run is-it-down-run-scheduled-checks --dry-run
```

Set environment variables:

- `IS_IT_DOWN_ENV`: `local`, `development`, or `production`.
- `IS_IT_DOWN_BIGQUERY_PROJECT_ID`: GCP project for BigQuery writes (optional if ADC project is set).
- `IS_IT_DOWN_BIGQUERY_DATASET_ID`: defaults to `is_it_down`.
- `IS_IT_DOWN_BIGQUERY_TABLE_ID`: defaults to `check_results`.

## Project Layout

- `src/is_it_down/checkers`: async checker framework + service checks.
- `src/is_it_down/scripts/run_service_checker.py`: ad-hoc checker runner.
- `src/is_it_down/scripts/run_scheduled_checks.py`: Cloud Run Job entrypoint writing to BigQuery.
- `infra/terraform`: Cloud Run Job, Cloud Scheduler trigger, BigQuery dataset/table.
- `.github/workflows/deploy.yml`: image build + Terraform deploy.

## GitHub Secrets

- `GCP_SA_KEY` (create this secret in each GitHub Environment: `dev` and `prod`)

## Deployment Workflow

- Any push to `main` (including direct pushes and merged PRs) deploys to `dev` (`is-it-down-dev`).
- Publishing a GitHub Release deploys to `prod` (`is-it-down-prod`).
- CI builds and pushes three images (`checker`, `api`, `web`) tagged with the commit SHA.
- Terraform applies the same tag to Cloud Run Job + Cloud Run Services.
