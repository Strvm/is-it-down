resource "google_project_service" "required" {
  for_each = toset([
    "artifactregistry.googleapis.com",
    "bigquery.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudscheduler.googleapis.com",
    "storage.googleapis.com",
    "run.googleapis.com",
    "cloudresourcemanager.googleapis.com",
  ])

  project = var.project[terraform.workspace]
  service = each.value

  disable_on_destroy = false
}
