import airflow
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator

from error_handling.settings import Settings

settings = Settings()

QUERY_WITH_ERROR = "SELECT * FROM toto"

with airflow.DAG(
        "dag",
        default_args=settings.dag_default_args,
        schedule_interval=None) as dag:
    compute_and_insert_team_stats_domain = BigQueryInsertJobOperator(
        task_id='compute_team_stats_domain',
        configuration={
            "query": {
                "query": QUERY_WITH_ERROR,
                "useLegacySql": False
            }
        },
        location='EU'
    )

    compute_and_insert_team_stats_domain
