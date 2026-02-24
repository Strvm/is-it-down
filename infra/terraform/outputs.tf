output "api_url" {
  value = google_cloud_run_v2_service.api.uri
}

output "cloudsql_connection_name" {
  value = google_sql_database_instance.postgres.connection_name
}
