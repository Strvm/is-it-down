resource "google_service_account" "github_actions_service_account" {
  project      = var.project
  account_id   = "github-actions-sa"
  display_name = "Github Actions Service Account"
}

locals {
  github_actions_project_roles = toset([
    "roles/artifactregistry.writer",
    "roles/cloudscheduler.admin",
    "roles/run.admin",
    "roles/bigquery.admin",
    "roles/iam.serviceAccountAdmin",
    "roles/resourcemanager.projectIamAdmin",
    "roles/compute.admin",
    "roles/vpcaccess.admin",
  ])
}

resource "google_project_iam_member" "github_actions_permissions" {
  for_each = local.github_actions_project_roles

  project = var.project
  role    = each.value
  member  = "serviceAccount:${google_service_account.github_actions_service_account.email}"
}

resource "google_service_account_iam_member" "github_can_act_as_runtime_sa" {
  count = var.runtime_service_account_id == null ? 0 : 1

  service_account_id = var.runtime_service_account_id
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.github_actions_service_account.email}"
}

resource "google_project_iam_member" "github_can_use_service_accounts" {
  project = var.project
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.github_actions_service_account.email}"
}
