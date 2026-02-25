module "iam" {
  source = "./iam"

  project                    = var.project[terraform.workspace]
  runtime_service_account_id = google_service_account.checker_runtime.name
}
