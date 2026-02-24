terraform {
  required_version = ">= 1.7.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_sql_database_instance" "postgres" {
  name             = var.database_instance_name
  region           = var.region
  database_version = "POSTGRES_16"

  settings {
    tier = "db-custom-2-7680"

    backup_configuration {
      enabled = true
    }

    ip_configuration {
      ipv4_enabled = true
    }
  }

  deletion_protection = true
}

resource "google_sql_database" "app" {
  name     = var.database_name
  instance = google_sql_database_instance.postgres.name
}

resource "google_sql_user" "app" {
  name     = var.database_user
  instance = google_sql_database_instance.postgres.name
  password = var.database_password
}

resource "google_service_account" "api" {
  account_id   = "is-it-down-api"
  display_name = "is-it-down API"
}

resource "google_service_account" "scheduler" {
  account_id   = "is-it-down-scheduler"
  display_name = "is-it-down Scheduler"
}

resource "google_service_account" "worker" {
  account_id   = "is-it-down-worker"
  display_name = "is-it-down Worker"
}

locals {
  database_url = "postgresql+asyncpg://${var.database_user}:${var.database_password}@/${var.database_name}?host=/cloudsql/${google_sql_database_instance.postgres.connection_name}"
}

resource "google_cloud_run_v2_service" "api" {
  name     = "is-it-down-api"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.api.email

    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [google_sql_database_instance.postgres.connection_name]
      }
    }

    containers {
      image = var.api_image

      ports {
        container_port = 8080
      }

      env {
        name  = "IS_IT_DOWN_ENV"
        value = "production"
      }

      env {
        name  = "IS_IT_DOWN_DATABASE_URL"
        value = local.database_url
      }

      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }
    }
  }
}

resource "google_cloud_run_v2_service" "scheduler" {
  name     = "is-it-down-scheduler"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_INTERNAL_ONLY"

  template {
    service_account = google_service_account.scheduler.email

    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [google_sql_database_instance.postgres.connection_name]
      }
    }

    containers {
      image   = var.scheduler_image
      command = ["is-it-down-scheduler"]

      env {
        name  = "IS_IT_DOWN_ENV"
        value = "production"
      }

      env {
        name  = "IS_IT_DOWN_DATABASE_URL"
        value = local.database_url
      }

      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }
    }

    scaling {
      min_instance_count = 1
      max_instance_count = 1
    }
  }
}

resource "google_cloud_run_v2_service" "worker" {
  name     = "is-it-down-worker"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_INTERNAL_ONLY"

  template {
    service_account = google_service_account.worker.email

    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [google_sql_database_instance.postgres.connection_name]
      }
    }

    containers {
      image   = var.worker_image
      command = ["is-it-down-worker"]

      env {
        name  = "IS_IT_DOWN_ENV"
        value = "production"
      }

      env {
        name  = "IS_IT_DOWN_DATABASE_URL"
        value = local.database_url
      }

      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }
    }

    scaling {
      min_instance_count = 1
      max_instance_count = 10
    }
  }
}
