resource "google_bigquery_table" "dag_failure_table" {
  project    = var.project_id
  dataset_id = "mazlum_test"
  table_id   = "dag_failure"
  clustering = [
    "dagId",
    "taskId",
    "dagOperator"
  ]

  time_partitioning {
    type  = "DAY"
    field = "ingestionDate"
  }

  schema = file("${path.module}/resource/bigquery/schema/dag_failure.json")
}

resource "google_monitoring_notification_channel" "notification_channel_airflow_errors" {
  project      = var.project_id
  display_name = "GroupBees Airflow error handling notification channel"
  type         = "email"
  labels       = {
    email_address = "mtosun@groupbees.fr"
  }
}

resource "google_logging_metric" "logging_metrics_airflow_errors" {
  project     = var.project_id
  name        = "composer_dags_tasks_errors"
  filter      = "severity=ERROR AND resource.type=\"cloud_composer_environment\" AND textPayload =~ \"Error in a Airflow DAG managed by the failure callback\""
  description = "Metric for Cloud Composer DAGs errors. The purpose is a lob-based metric to intercept all the Airflow errors."
  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"

    labels {
      key         = "task_id"
      value_type  = "STRING"
      description = "Task ID of current Airflow task"
    }
    labels {
      key         = "execution_date"
      value_type  = "STRING"
      description = "Execution date of the current Airflow task"
    }
  }

  label_extractors = {
    "task_id"        = "EXTRACT(labels.\"task-id\")"
    "execution_date" = "EXTRACT(labels.\"execution-date\")"
  }
}

resource "google_monitoring_alert_policy" "alert_policies_airflow_errors" {
  depends_on = [
    google_monitoring_notification_channel.notification_channel_airflow_errors,
    google_logging_metric.logging_metrics_airflow_errors
  ]
  project      = var.project_id
  display_name = "composer_dags_tasks_errors"
  combiner     = "OR"
  conditions {
    display_name = "composer_dags_tasks_errors"
    condition_threshold {
      filter          = "metric.type=\"logging.googleapis.com/user/composer_dags_tasks_errors\" AND resource.type=\"cloud_composer_environment\""
      duration        = "0s"
      comparison      = "COMPARISON_GT"
      threshold_value = "0.9"
      trigger {
        count = 1
      }

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_COUNT"
      }
    }
  }
  documentation {
    content = "Alert sent when Airflow errors occurred in Cloud Composer logs."
  }

  notification_channels = [google_monitoring_notification_channel.notification_channel_airflow_errors.name]
}