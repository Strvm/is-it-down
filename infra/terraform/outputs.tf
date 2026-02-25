output "workspace" {
  value = terraform.workspace
}

output "project_id" {
  value = var.project[terraform.workspace]
}

output "cloud_run_job_name" {
  value = google_cloud_run_v2_job.checker.name
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
