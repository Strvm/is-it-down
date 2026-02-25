data "google_project" "current" {
  project_id = var.project[terraform.workspace]
}

locals {
  workspace_custom_domain = trimspace(lookup(var.custom_domain, terraform.workspace, ""))
  custom_domain_enabled   = local.workspace_custom_domain != ""
  web_custom_domain       = local.custom_domain_enabled ? local.workspace_custom_domain : null
  api_custom_domain       = local.custom_domain_enabled ? "${var.api_subdomain}.${local.workspace_custom_domain}" : null
  api_public_base_url     = local.custom_domain_enabled ? "https://${local.api_custom_domain}" : module.cloud_run_api_service.uri
}

resource "google_cloud_run_domain_mapping" "web" {
  count    = local.custom_domain_enabled ? 1 : 0
  location = var.region
  name     = local.web_custom_domain

  metadata {
    namespace = data.google_project.current.project_id
  }

  spec {
    route_name = module.cloud_run_web_service.name
  }

  depends_on = [
    google_project_service.required,
    module.cloud_run_web_service,
  ]
}

resource "google_cloud_run_domain_mapping" "api" {
  count    = local.custom_domain_enabled ? 1 : 0
  location = var.region
  name     = local.api_custom_domain

  metadata {
    namespace = data.google_project.current.project_id
  }

  spec {
    route_name = module.cloud_run_api_service.name
  }

  depends_on = [
    google_project_service.required,
    module.cloud_run_api_service,
  ]
}
