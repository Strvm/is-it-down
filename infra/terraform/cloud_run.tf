resource "google_service_account" "checker_runtime" {
  project      = var.project[terraform.workspace]
  account_id   = "is-it-down-checker"
  display_name = "is-it-down checker runtime"
}

resource "google_service_account" "api_runtime" {
  project      = var.project[terraform.workspace]
  account_id   = "is-it-down-api"
  display_name = "is-it-down api runtime"
}

resource "google_service_account" "web_runtime" {
  project      = var.project[terraform.workspace]
  account_id   = "is-it-down-web"
  display_name = "is-it-down web runtime"
}

resource "google_service_account" "job_trigger" {
  project      = var.project[terraform.workspace]
  account_id   = "is-it-down-job-trigger"
  display_name = "is-it-down job trigger"
}

resource "google_project_iam_member" "checker_bigquery_data_editor" {
  project = var.project[terraform.workspace]
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.checker_runtime.email}"
}

resource "google_project_iam_member" "checker_bigquery_job_user" {
  project = var.project[terraform.workspace]
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.checker_runtime.email}"
}

resource "google_project_iam_member" "api_bigquery_data_viewer" {
  project = var.project[terraform.workspace]
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${google_service_account.api_runtime.email}"
}

resource "google_project_iam_member" "api_bigquery_data_editor" {
  project = var.project[terraform.workspace]
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.api_runtime.email}"
}

resource "google_project_iam_member" "api_bigquery_job_user" {
  project = var.project[terraform.workspace]
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.api_runtime.email}"
}

resource "google_project_iam_member" "trigger_run_invoker" {
  project = var.project[terraform.workspace]
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.job_trigger.email}"
}

resource "google_cloud_run_v2_job" "checker" {
  name     = "is-it-down-checker-job"
  project  = var.project[terraform.workspace]
  location = var.region

  template {
    task_count  = var.checker_job_task_count
    parallelism = var.checker_job_task_count

    template {
      service_account = google_service_account.checker_runtime.email
      timeout         = "${var.job_timeout_seconds}s"
      max_retries     = var.job_max_retries

      containers {
        image   = "${var.region}-docker.pkg.dev/${var.project[terraform.workspace]}/${var.artifact_registry_repository}/${var.artifact_registry_image}:${var.image_tag}"
        command = ["is-it-down-run-scheduled-checks"]

        env {
          name  = "IS_IT_DOWN_ENV"
          value = var.app_env[terraform.workspace]
        }

        env {
          name  = "IS_IT_DOWN_LOG_LEVEL"
          value = var.log_level
        }

        env {
          name  = "IS_IT_DOWN_CHECKER_CONCURRENCY"
          value = tostring(var.checker_concurrency)
        }

        env {
          name  = "IS_IT_DOWN_BIGQUERY_PROJECT_ID"
          value = var.project[terraform.workspace]
        }

        env {
          name  = "IS_IT_DOWN_BIGQUERY_DATASET_ID"
          value = var.bigquery_dataset_id
        }

        env {
          name  = "IS_IT_DOWN_BIGQUERY_TABLE_ID"
          value = var.bigquery_table_id
        }

        env {
          name  = "IS_IT_DOWN_PROXY_SECRET_PROJECT_ID"
          value = var.project[terraform.workspace]
        }

        env {
          name  = "IS_IT_DOWN_DEFAULT_CHECKER_PROXY_SECRET_ID"
          value = var.checker_proxy_secret_id
        }

        env {
          name  = "IS_IT_DOWN_REDIS_SECRET_PROJECT_ID"
          value = var.project[terraform.workspace]
        }

        env {
          name  = "IS_IT_DOWN_API_CACHE_REDIS_SECRET_ID"
          value = var.api_cache_redis_secret_id
        }

        env {
          name  = "IS_IT_DOWN_API_CACHE_ENABLED"
          value = tostring(var.api_cache_enabled)
        }

        env {
          name  = "IS_IT_DOWN_API_CACHE_TTL_SECONDS"
          value = tostring(var.api_cache_ttl_seconds)
        }

        env {
          name  = "IS_IT_DOWN_API_CACHE_KEY_PREFIX"
          value = var.api_cache_key_prefix
        }

        env {
          name  = "IS_IT_DOWN_API_CACHE_WARM_ON_CHECKER_JOB"
          value = tostring(var.api_cache_warm_on_checker_job)
        }

        env {
          name  = "IS_IT_DOWN_API_CACHE_WARM_ON_CLOUD_RUN_CHECKER_JOB"
          value = tostring(var.api_cache_warm_on_cloud_run_checker_job)
        }

        env {
          name  = "IS_IT_DOWN_API_CACHE_WARM_IMPACTED_SERVICE_LIMIT"
          value = tostring(var.api_cache_warm_impacted_service_limit)
        }

        env {
          name  = "IS_IT_DOWN_API_CACHE_WARM_TOP_VIEWED_SERVICE_LIMIT"
          value = tostring(var.api_cache_warm_top_viewed_service_limit)
        }
      }
    }
  }

  depends_on = [
    google_project_service.required,
    google_artifact_registry_repository.checker_images,
    google_bigquery_table.check_results,
    google_secret_manager_secret.checker_proxy,
    google_secret_manager_secret_iam_member.checker_proxy_accessor,
    google_secret_manager_secret.api_cache_redis,
    google_secret_manager_secret_iam_member.api_cache_redis_accessor_checker,
    google_project_iam_member.checker_bigquery_data_editor,
    google_project_iam_member.checker_bigquery_job_user,
  ]
}

module "cloud_run_api_service" {
  source = "./modules/cloud_run_service"

  project               = var.project[terraform.workspace]
  region                = var.region
  name                  = var.api_service_name
  image                 = "${var.region}-docker.pkg.dev/${var.project[terraform.workspace]}/${var.artifact_registry_repository}/${var.artifact_registry_api_image}:${var.image_tag}"
  service_account_email = google_service_account.api_runtime.email
  default_uri_disabled  = terraform.workspace == "prod" && local.custom_domain_enabled
  min_instance_count    = 0
  container_port        = 8080
  allow_public_invoker  = true
  env_vars = {
    IS_IT_DOWN_ENV                          = var.app_env[terraform.workspace]
    IS_IT_DOWN_LOG_LEVEL                    = var.log_level
    IS_IT_DOWN_BIGQUERY_PROJECT_ID          = var.project[terraform.workspace]
    IS_IT_DOWN_BIGQUERY_DATASET_ID          = var.bigquery_dataset_id
    IS_IT_DOWN_BIGQUERY_TABLE_ID            = var.bigquery_table_id
    IS_IT_DOWN_TRACKING_BIGQUERY_DATASET_ID = var.tracking_bigquery_dataset_id
    IS_IT_DOWN_TRACKING_BIGQUERY_TABLE_ID   = var.tracking_bigquery_table_id
    IS_IT_DOWN_REDIS_SECRET_PROJECT_ID      = var.project[terraform.workspace]
    IS_IT_DOWN_API_CACHE_REDIS_SECRET_ID    = var.api_cache_redis_secret_id
    IS_IT_DOWN_API_CACHE_ENABLED            = tostring(var.api_cache_enabled)
    IS_IT_DOWN_API_CACHE_TTL_SECONDS        = tostring(var.api_cache_ttl_seconds)
    IS_IT_DOWN_API_CACHE_KEY_PREFIX         = var.api_cache_key_prefix
  }

  depends_on = [
    google_project_service.required,
    google_artifact_registry_repository.checker_images,
    google_bigquery_table.check_results,
    google_bigquery_table.service_detail_views,
    google_secret_manager_secret.api_cache_redis,
    google_secret_manager_secret_iam_member.api_cache_redis_accessor_api,
    google_project_iam_member.api_bigquery_data_viewer,
    google_project_iam_member.api_bigquery_data_editor,
    google_project_iam_member.api_bigquery_job_user,
  ]
}

module "cloud_run_web_service" {
  source = "./modules/cloud_run_service"

  project               = var.project[terraform.workspace]
  region                = var.region
  name                  = var.web_service_name
  image                 = "${var.region}-docker.pkg.dev/${var.project[terraform.workspace]}/${var.artifact_registry_repository}/${var.artifact_registry_web_image}:${var.image_tag}"
  service_account_email = google_service_account.web_runtime.email
  default_uri_disabled  = terraform.workspace == "prod" && local.custom_domain_enabled
  min_instance_count    = 0
  container_port        = 8080
  allow_public_invoker  = true
  env_vars = {
    API_BASE_URL             = local.api_public_base_url
    NEXT_PUBLIC_API_BASE_URL = local.api_public_base_url
  }

  depends_on = [
    google_project_service.required,
    google_artifact_registry_repository.checker_images,
    module.cloud_run_api_service,
  ]
}

resource "google_cloud_scheduler_job" "run_checker" {
  name      = "is-it-down-checker-trigger"
  project   = var.project[terraform.workspace]
  region    = var.region
  schedule  = var.checker_schedule
  time_zone = var.checker_schedule_time_zone

  http_target {
    http_method = "POST"
    uri         = "https://run.googleapis.com/v2/projects/${var.project[terraform.workspace]}/locations/${var.region}/jobs/${google_cloud_run_v2_job.checker.name}:run"

    oauth_token {
      service_account_email = google_service_account.job_trigger.email
      scope                 = "https://www.googleapis.com/auth/cloud-platform"
    }
  }

  retry_config {
    retry_count          = var.schedule_retry_count
    min_backoff_duration = "10s"
    max_backoff_duration = "300s"
    max_doublings        = 3
  }

  depends_on = [
    google_cloud_run_v2_job.checker,
    google_project_iam_member.trigger_run_invoker,
  ]
}
