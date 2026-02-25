resource "google_secret_manager_secret" "checker_proxy" {
  project   = var.project[terraform.workspace]
  secret_id = var.checker_proxy_secret_id

  replication {
    auto {}
  }

  depends_on = [google_project_service.required]
}

resource "google_secret_manager_secret_version" "checker_proxy" {
  count = trimspace(var.checker_proxy_secret_value) == "" ? 0 : 1

  secret      = google_secret_manager_secret.checker_proxy.id
  secret_data = var.checker_proxy_secret_value
}

resource "google_secret_manager_secret_iam_member" "checker_proxy_accessor" {
  project   = var.project[terraform.workspace]
  secret_id = google_secret_manager_secret.checker_proxy.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.checker_runtime.email}"
}
