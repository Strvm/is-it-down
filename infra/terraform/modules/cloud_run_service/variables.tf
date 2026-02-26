variable "project" {
  type = string
}

variable "region" {
  type = string
}

variable "name" {
  type = string
}

variable "image" {
  type = string
}

variable "service_account_email" {
  type = string
}

variable "min_instance_count" {
  type    = number
  default = 0
}

variable "container_port" {
  type    = number
  default = 8080
}

variable "env_vars" {
  type    = map(string)
  default = {}
}

variable "allow_public_invoker" {
  type    = bool
  default = false
}

variable "default_uri_disabled" {
  type    = bool
  default = false
}
