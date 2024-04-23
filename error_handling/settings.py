import os
from dataclasses import dataclass
from datetime import timedelta

from airflow.utils.dates import days_ago

from error_handling.failure_callback import task_failure_callback


@dataclass
class Settings:
    dag_default_args = {
        'depends_on_past': False,
        'email': ['airflow@example.com'],
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 0,
        'retry_delay': timedelta(minutes=5),
        "start_date": days_ago(1),
        "on_failure_callback": task_failure_callback

    }
    project_id = os.getenv("GCP_PROJECT")
