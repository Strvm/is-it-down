resource "google_bigquery_dataset" "results" {
  project    = var.project[terraform.workspace]
  dataset_id = var.bigquery_dataset_id
  location   = var.bigquery_location

  delete_contents_on_destroy = var.bigquery_delete_contents_on_destroy

  depends_on = [google_project_service.required]
}

resource "google_bigquery_table" "check_results" {
  project    = var.project[terraform.workspace]
  dataset_id = google_bigquery_dataset.results.dataset_id
  table_id   = var.bigquery_table_id

  time_partitioning {
    type  = "DAY"
    field = "observed_at"
  }

  clustering = ["service_key", "status"]

  schema = jsonencode([
    {
      name = "run_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "execution_id"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "service_key"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "checker_class"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "check_key"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "status"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "observed_at"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name = "latency_ms"
      type = "INT64"
      mode = "NULLABLE"
    },
    {
      name = "http_status"
      type = "INT64"
      mode = "NULLABLE"
    },
    {
      name = "error_code"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "error_message"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "metadata_json"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "ingested_at"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    }
  ])
}

resource "google_bigquery_dataset" "tracking" {
  project    = var.project[terraform.workspace]
  dataset_id = var.tracking_bigquery_dataset_id
  location   = var.bigquery_location

  delete_contents_on_destroy = var.bigquery_delete_contents_on_destroy

  depends_on = [google_project_service.required]
}

resource "google_bigquery_table" "service_detail_views" {
  project    = var.project[terraform.workspace]
  dataset_id = google_bigquery_dataset.tracking.dataset_id
  table_id   = var.tracking_bigquery_table_id

  time_partitioning {
    type  = "DAY"
    field = "viewed_at"
  }

  clustering = ["service_key"]

  schema = jsonencode([
    {
      name = "event_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "service_key"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "request_path"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "request_method"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "user_agent"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "referer"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "client_ip"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "viewed_at"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name = "ingested_at"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    }
  ])
}
