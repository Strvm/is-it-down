terraform {

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.21.0"
    }
  }

  backend "gcs" {
    bucket = "is-it-down-terraform-states"
    prefix = "terraform/state"
  }
}
