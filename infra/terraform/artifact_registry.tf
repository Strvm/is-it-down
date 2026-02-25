resource "google_artifact_registry_repository" "checker_images" {
  project       = var.project[terraform.workspace]
  location      = var.region
  repository_id = var.artifact_registry_repository
  description   = "Container images for the is-it-down checker job"
  format        = "DOCKER"

  depends_on = [google_project_service.required]
}
