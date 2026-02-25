provider "google" {
  project = var.project[terraform.workspace]
  region  = var.region
}
