from __future__ import annotations

import logging
import traceback
from datetime import datetime

from airflow.exceptions import AirflowException
from google.cloud import bigquery

DATASET_ID = "mazlum_test"
JOB_FAILURE_TABLE = "dag_failure"
DEFAULT_EXCEPTION_NAME = AirflowException.__name__


def _get_exception_traceback(exception: BaseException | str) -> str:
    if isinstance(exception, BaseException):
        return ''.join(traceback.format_exception(None, exception, exception.__traceback__))
    else:
        return str(exception)


def _get_exception_name(exception: BaseException | str) -> str:
    return type(exception).__name__ if isinstance(exception, BaseException) else DEFAULT_EXCEPTION_NAME


def task_failure_callback(context):
    logging.info('#############################Context')
    logging.info(context)
    logging.info('#############################')

    ti = context['task_instance']
    exception = context['exception']

    failure_info = {
        "dagId": ti.dag_id,
        "taskId": ti.task_id,
        "dagOperator": ti.operator,
        "exceptionName": _get_exception_name(exception),
        "exceptionTraceback": _get_exception_traceback(exception),
        "logUrl": ti.log_url,
        "creationDate": datetime.now()
    }
    logging.error(f"##### Error in Airflow DAG in the failure callback ##### !!!!! \n Failure info : {failure_info}")

    client = bigquery.Client()

    client.insert_rows_json(
        f'{DATASET_ID}.{JOB_FAILURE_TABLE}',
        [failure_info]
    )
