resource "google_cloud_run_v2_service" "this" {
  name     = var.name
  project  = var.project
  location = var.region

  template {
    service_account = var.service_account_email

    scaling {
      min_instance_count = var.min_instance_count
    }

    containers {
      image = var.image

      ports {
        container_port = var.container_port
      }

      dynamic "env" {
        for_each = var.env_vars
        content {
          name  = env.key
          value = env.value
        }
      }
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  count = var.allow_public_invoker ? 1 : 0

  project  = var.project
  location = var.region
  name     = google_cloud_run_v2_service.this.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
