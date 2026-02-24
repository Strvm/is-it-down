variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "database_instance_name" {
  type    = string
  default = "is-it-down-postgres"
}

variable "database_name" {
  type    = string
  default = "is_it_down"
}

variable "database_user" {
  type    = string
  default = "is_it_down"
}

variable "database_password" {
  type      = string
  sensitive = true
}

variable "api_image" {
  type = string
}

variable "scheduler_image" {
  type = string
}

variable "worker_image" {
  type = string
}
