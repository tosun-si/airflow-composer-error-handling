import airflow
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator

from error_handling.settings import Settings

settings = Settings()

QUERY_WITH_ERROR = "SELECT * FROM toto"

with airflow.DAG(
        "dag_with_bq_error",
        default_args=settings.dag_default_args,
        schedule_interval=None) as dag:
    query_with_error = BigQueryInsertJobOperator(
        task_id='query_with_error',
        configuration={
            "query": {
                "query": QUERY_WITH_ERROR,
                "useLegacySql": False
            }
        },
        location='EU'
    )

    query_with_error
