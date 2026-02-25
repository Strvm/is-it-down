terraform {

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }

  backend "gcs" {
    bucket = "is-it-down-terraform-states"
    prefix = "terraform/state"
  }
}
