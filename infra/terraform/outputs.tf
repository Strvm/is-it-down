output "workspace" {
  value = terraform.workspace
}

output "project_id" {
  value = var.project[terraform.workspace]
}

output "cloud_run_job_name" {
  value = google_cloud_run_v2_job.checker.name
}

output "cloud_run_api_service_name" {
  value = module.cloud_run_api_service.name
}

output "cloud_run_web_service_name" {
  value = module.cloud_run_web_service.name
}

output "cloud_run_api_url" {
  value = module.cloud_run_api_service.uri
}

output "cloud_run_web_url" {
  value = module.cloud_run_web_service.uri
}

output "cloud_scheduler_job_name" {
  value = google_cloud_scheduler_job.run_checker.name
}

output "bigquery_dataset_id" {
  value = google_bigquery_dataset.results.dataset_id
}

output "bigquery_table_id" {
  value = google_bigquery_table.check_results.table_id
}

output "checker_runtime_service_account" {
  value = google_service_account.checker_runtime.email
}

output "api_runtime_service_account" {
  value = google_service_account.api_runtime.email
}

output "web_runtime_service_account" {
  value = google_service_account.web_runtime.email
}

output "artifact_registry_repository" {
  value = google_artifact_registry_repository.checker_images.repository_id
}
