# is-it-down Design Proposal

## Summary

`is-it-down` is an open-source outage intelligence platform built in Python. It runs async OOP checkers against real service APIs, computes health scores, and adds dependency-aware attribution when failures correlate.

## Key Decisions

- Python `>=3.13` with `uv` package manager.
- FastAPI public API with REST + SSE.
- Separate scheduler and worker Cloud Run services.
- Postgres-only persistence on GCP Cloud SQL (v1).
- Monorepo-based checker contributions.
- Single-region runtime (v1).
- 30-60 second check cadence target.

## Architecture

- **API service**: read-only status endpoints and SSE stream.
- **Scheduler service**: enqueues due check jobs into Postgres queue tables.
- **Worker service**: leases jobs, executes async checks, writes runs/snapshots/incidents.
- **Postgres**: source of truth for config, jobs, results, snapshots, and incidents.

## OOP Checker Model

- `BaseCheck`: abstract async endpoint checker contract.
- `BaseServiceChecker`: composes multiple checks for one service.
- Concrete checker classes in `src/is_it_down/checkers/services/*`.

## Scoring

- Check status maps to numeric score (`up`, `degraded`, `down`).
- Service raw score is weighted average of checks.
- Service status thresholds:
  - `>=95`: up
  - `70-94`: degraded
  - `<70`: down

## Dependency Attribution

When a service is degraded/down and one or more dependencies are also degraded/down in the same observation window, snapshots are flagged as `dependency_impacted` and a probable root dependency is selected with confidence.

## API Endpoints (v1)

- `GET /v1/services`
- `GET /v1/services/{slug}`
- `GET /v1/services/{slug}/history?window=24h`
- `GET /v1/incidents?status=open`
- `GET /v1/stream` (SSE)

## Deployment

- Infra via Terraform (`infra/terraform`).
- API/scheduler/worker deploy to Cloud Run.
- CI/CD via GitHub Actions.

## Testing

- Unit tests: scoring, attribution, utilities.
- Contract tests: checker interfaces and result shape.
- Integration tests: scheduler/worker/API data flow (next phase).
