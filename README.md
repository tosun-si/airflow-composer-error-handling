# airflow-composer-error-handling

This project shows how to apply error handling in Airflow DAGs and Cloud Composer in Google Cloud.\
Instead of repeat a technical code of error handling in each DAG, the principle is to use a callback and\
a failure interceptor.

The advantage of this approach in to not pollute DAGs with techincal code concerning error handling and use\
separation of concern and a centralized code.

An alert will be fired in real time on each DAG error, and email will be sent.\
This alert will be created will Cloud Monitoring in GCP, via Terraform and Cloud Build.

![etl_batch_pipeline_composer_dataflow_bq.png](diagram%2Fetl_batch_pipeline_composer_dataflow_bq.png)

The article on this topic :

https://medium.com/google-cloud/etl-batch-pipeline-with-cloud-storage-dataflow-and-bigquery-orchestrated-by-airflow-composer-896625aed586

The video in English :

https://youtu.be/Ps6zllstpVk

The video in French :

https://youtu.be/QcQxEbRjo5o

## Run job with Dataflow runner from local machine :

```bash
python -m team_league.application.team_league_app \
    --project=gb-poc-373711 \
    --project_id=gb-poc-373711 \
    --input_json_file=gs://mazlum_dev/team_league/input/json/input_teams_stats_raw.json \
    --job_name=team-league-python-job-$(date +'%Y-%m-%d-%H-%M-%S') \
    --runner=DataflowRunner \
    --staging_location=gs://mazlum_dev/dataflow/staging \
    --region=europe-west1 \
    --setup_file=./setup.py \
    --temp_location=gs://mazlum_dev/dataflow/temp \
    --team_league_dataset="mazlum_test" \
    --team_stats_table="team_stat"
```

## Set env vars in your Shell

```shell
# Common
export PROJECT_ID={{your_project_id}}
export LOCATION={{your_location}}

# Dataflow (deployment Flex Template)
export REPO_NAME=internal-images
export IMAGE_NAME="dataflow/team-league-elt-dataflow-python"
export IMAGE_TAG=latest
export METADATA_FILE="config/dataflow_template_metadata.json"
export METADATA_TEMPLATE_FILE_PATH="gs://mazlum_dev/dataflow/templates/team_league/python/team-league-elt-dataflow-python.json"
export SDK_LANGUAGE=PYTHON

# Composer (deployment DAG)
export DAG_FOLDER=dag
export COMPOSER_ENVIRONMENT=dev-composer-env
export CONFIG_FOLDER_NAME=config
export ENV=dev
```

## Deploy the Dataflow Flex template with Cloud Build from local machine

```shell
gcloud builds submit \
    --project=$PROJECT_ID \
    --region=$LOCATION \
    --config deploy-dataflow-flex-template.yaml \
    --substitutions _REPO_NAME="$REPO_NAME",_IMAGE_NAME="$IMAGE_NAME",_IMAGE_TAG="$IMAGE_TAG",_METADATA_TEMPLATE_FILE_PATH="$METADATA_TEMPLATE_FILE_PATH",_SDK_LANGUAGE="$SDK_LANGUAGE",_METADATA_FILE="$METADATA_FILE" \
    --verbosity="debug" .
```

## Deploy the Dataflow Flex template with Cloud Build manual trigger on Github repository : build Docker image and create template spec file

```bash
gcloud beta builds triggers create manual \
    --project=$PROJECT_ID \
    --region=$LOCATION \
    --name="deploy-dataflow-template-team-league-python-dockerfile" \
    --repo="https://github.com/tosun-si/dataflow-python-ci-cd" \
    --repo-type="GITHUB" \
    --branch="main" \
    --build-config="deploy-dataflow-flex-template.yaml" \
    --substitutions _REPO_NAME="$REPO_NAME",_IMAGE_NAME="$IMAGE_NAME",_IMAGE_TAG="$IMAGE_TAG",_METADATA_TEMPLATE_FILE_PATH="$METADATA_TEMPLATE_FILE_PATH",_SDK_LANGUAGE="$SDK_LANGUAGE",_METADATA_FILE="$METADATA_FILE" \
    --verbosity="debug"
```

## Deploy the Airflow DAG in Composer with Cloud Build from the local machine

```shell
gcloud builds submit \
    --project=$PROJECT_ID \
    --region=$LOCATION \
    --config deploy-airflow-dag.yaml \
    --substitutions _DAG_FOLDER="$DAG_FOLDER",_COMPOSER_ENVIRONMENT="$COMPOSER_ENVIRONMENT",_CONFIG_FOLDER_NAME="$CONFIG_FOLDER_NAME",_ENV="$ENV" \
    --verbosity="debug" .
```

## Deploy the Airflow DAG in Composer with a Cloud Build manual trigger :

```bash
gcloud beta builds triggers create manual \
    --project=$PROJECT_ID \
    --region=$LOCATION \
    --name="deploy-airflow-dag-dataflow-elt-team-stats" \
    --repo="https://github.com/tosun-si/teams-league-airflow-dataflow-etl" \
    --repo-type="GITHUB" \
    --branch="main" \
    --build-config="deploy-airflow-dag.yaml" \
    --substitutions _DAG_FOLDER="$DAG_FOLDER",_COMPOSER_ENVIRONMENT="$COMPOSER_ENVIRONMENT",_CONFIG_FOLDER_NAME="$CONFIG_FOLDER_NAME",_ENV="$ENV" \
    --verbosity="debug"
```

