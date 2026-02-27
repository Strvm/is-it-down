# Terraform Layout

This directory is a single Terraform root that uses workspaces for environments:

- `dev` -> `var.project["dev"]`
- `prod` -> `var.project["prod"]`

Project IDs are configured with:

```hcl
variable "project" {
  type = map(string)
  default = {
    dev  = "is-it-down-dev"
    prod = "is-it-down-prod"
  }
}
```

and referenced as `var.project[terraform.workspace]`.

File layout:

- `main.tf`: terraform/version/backend block only
- `provider.tf`: Google provider config
- `checks.tf`: workspace guardrails
- `project_services.tf`: required GCP APIs
- `bigquery.tf`: BigQuery dataset/table for checker results
- `secret_manager.tf`: Secret Manager secrets for checker proxy URL and API cache Redis URL + IAM accessor bindings
- `cloud_run.tf`: Cloud Run Job + Cloud Run Services + Cloud Scheduler trigger + IAM/service accounts
- `custom_domains.tf`: optional Cloud Run custom domain mappings for web/API
- `modules/cloud_run_service`: reusable module for Cloud Run Service resources (API/web)

## What gets created

- BigQuery dataset + partitioned table for check results
- Secret Manager secret for checker proxy URL
- Secret Manager secret for API Redis cache URL
- Cloud Run Job to execute `is-it-down-run-scheduled-checks`
- Cloud Run Service for FastAPI backend (`is-it-down-api`)
- Cloud Run Service for Next.js frontend (`is-it-down-web`)
- Optional custom domain mappings for web root + API subdomain
- Cloud Scheduler cron trigger that calls `jobs:run`
- Service accounts and IAM for runtime/trigger

Checker job defaults:

- `checker_job_task_count = 4` (Cloud Run Job tasks and parallelism)
- `api_cache_warm_on_cloud_run_checker_job = true` (cache warming remains enabled in checker tasks)

## Example: dev apply

```bash
cd infra/terraform
terraform init \
  -backend-config="configs/config.dev.tfbackend"

terraform workspace select dev || terraform workspace new dev

terraform apply \
  -var "image_tag=latest" \
  -var "checker_proxy_secret_value=http://username:password@proxy.example:8080" \
  -var "api_cache_redis_secret_value=rediss://default:password@your-upstash-host:6379"
```

## Custom domains (web + API)

Set a root domain for the current workspace with `custom_domain`. Terraform maps:

- web service -> `<custom_domain>`
- api service -> `<api_subdomain>.<custom_domain>` (default `api`)
- In `prod`, the default Cloud Run `*.run.app` URL is disabled for both services when a custom domain is configured.

Prerequisite: verify ownership of the root domain in Google Search Console for the same GCP project before applying domain mappings.

Example for prod:

```bash
terraform workspace select prod
terraform apply \
  -var 'image_tag=latest'
```

`custom_domain` defaults to:

```hcl
{
  dev  = ""
  prod = "is-it-down.dev"
}
```

After apply, use these outputs to configure DNS at your registrar:

- `web_custom_domain_dns_records`
- `api_custom_domain_dns_records`

You can inspect them with:

```bash
terraform output web_custom_domain_dns_records
terraform output api_custom_domain_dns_records
```
