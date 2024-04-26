import airflow
from airflow.operators.python import PythonOperator

from error_handling.settings import Settings

settings = Settings()


def validate_input_param(**kwargs) -> None:
    dag_run_conf = kwargs['dag_run'].conf or {}
    input_param: str = dag_run_conf.get('input_param')

    if input_param is None:
        raise ValueError("The required input param is missing")


with airflow.DAG(
        "dag_without_required_input_param_error",
        default_args=settings.dag_default_args,
        schedule_interval=None) as dag:
    validate_input_param = PythonOperator(
        task_id='validate_input_param',
        python_callable=validate_input_param,
        provide_context=True)

    validate_input_param
