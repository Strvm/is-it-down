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
