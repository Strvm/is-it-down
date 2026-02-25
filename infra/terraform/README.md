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
- `cloud_run.tf`: Cloud Run Job, Cloud Scheduler trigger, and IAM/service accounts

## What gets created

- BigQuery dataset + partitioned table for check results
- Cloud Run Job to execute `is-it-down-run-scheduled-checks`
- Cloud Scheduler cron trigger that calls `jobs:run`
- Service accounts and IAM for runtime/trigger

## Example: dev apply

```bash
cd infra/terraform
terraform init \
  -backend-config="configs/config.dev.tfbackend"

terraform workspace select dev || terraform workspace new dev

terraform apply -var "image_tag=latest"
```
