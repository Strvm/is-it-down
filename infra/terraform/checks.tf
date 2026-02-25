check "workspace_is_configured" {
  assert {
    condition     = contains(keys(var.project), terraform.workspace)
    error_message = "Workspace '${terraform.workspace}' is not configured in var.project."
  }
}

check "workspace_has_app_env" {
  assert {
    condition     = contains(keys(var.app_env), terraform.workspace)
    error_message = "Workspace '${terraform.workspace}' is not configured in var.app_env."
  }
}
