variable "region" {
  type    = string
  default = "us-central1"
}

variable "project" {
  type = map(string)
  default = {
    dev  = "is-it-down-dev"
    prod = "is-it-down-prod"
  }
}

variable "app_env" {
  type = map(string)
  default = {
    dev  = "development"
    prod = "production"
  }
}

variable "image_tag" {
  type        = string
  default     = "latest"
  description = "Container image tag for the checker job image."
}

variable "artifact_registry_repository" {
  type    = string
  default = "is-it-down"
}

variable "artifact_registry_image" {
  type    = string
  default = "is-it-down-checker"
}

variable "artifact_registry_api_image" {
  type    = string
  default = "is-it-down-api"
}

variable "artifact_registry_web_image" {
  type    = string
  default = "is-it-down-web"
}

variable "api_service_name" {
  type    = string
  default = "is-it-down-api"
}

variable "web_service_name" {
  type    = string
  default = "is-it-down-web"
}

variable "bigquery_dataset_id" {
  type    = string
  default = "is_it_down"
}

variable "bigquery_table_id" {
  type    = string
  default = "check_results"
}

variable "tracking_bigquery_dataset_id" {
  type    = string
  default = "is_it_down_tracking"
}

variable "tracking_bigquery_table_id" {
  type    = string
  default = "service_detail_views"
}

variable "checker_proxy_secret_id" {
  type        = string
  default     = "checker-proxy-url"
  description = "Secret Manager secret ID storing checker proxy URL."
}

variable "checker_proxy_secret_value" {
  type        = string
  default     = ""
  sensitive   = true
  description = "Optional initial proxy URL secret payload. Set on first apply to provision a usable secret version."
}

variable "api_cache_redis_secret_id" {
  type        = string
  default     = "api-cache-redis-url"
  description = "Secret Manager secret ID storing API cache Redis URL."
}

variable "api_cache_redis_secret_value" {
  type        = string
  default     = ""
  sensitive   = true
  description = "Optional initial Redis URL secret payload. Set on first apply to provision a usable secret version."
}

variable "bigquery_location" {
  type    = string
  default = "US"
}

variable "bigquery_delete_contents_on_destroy" {
  type    = bool
  default = false
}

variable "checker_schedule" {
  type    = string
  default = "*/10 * * * *"
}

variable "checker_schedule_time_zone" {
  type    = string
  default = "Etc/UTC"
}

variable "schedule_retry_count" {
  type    = number
  default = 3
}

variable "job_timeout_seconds" {
  type    = number
  default = 600
}

variable "job_max_retries" {
  type    = number
  default = 1
}

variable "log_level" {
  type    = string
  default = "INFO"
}

variable "checker_concurrency" {
  type    = number
  default = 10
}



variable "checker_job_task_count" {
  type = map(string)
  default = {
    dev  = 1
    prod = 2
  }
}

variable "api_cache_enabled" {
  type    = bool
  default = true
}

variable "api_cache_ttl_seconds" {
  type    = number
  default = 600
}

variable "api_cache_key_prefix" {
  type    = string
  default = "is-it-down:api:v1"
}

variable "api_cache_warm_on_checker_job" {
  type    = bool
  default = true
}

variable "api_cache_warm_on_cloud_run_checker_job" {
  type    = bool
  default = true
}

variable "api_cache_warm_impacted_service_limit" {
  type    = number
  default = 25
}

variable "api_cache_warm_top_viewed_service_limit" {
  type    = number
  default = 25
}

variable "custom_domain" {
  type = map(string)
  default = {
    dev  = ""
    prod = "is-it-down.dev"
  }
  description = "Root domain per workspace. Set to empty string to disable Cloud Run domain mappings."
}

variable "api_subdomain" {
  type        = string
  default     = "api"
  description = "Subdomain prefix for the API custom domain (for example: api.example.com)."
}
