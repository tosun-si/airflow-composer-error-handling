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

## Set env vars in your Shell

```shell
# Common
export PROJECT_ID={{project_id}}
export LOCATION={{region}}

# Composer (deployment DAG)
export DAG_FOLDER=error_handling
export COMPOSER_ENVIRONMENT=dev-composer-env
export ENV=dev

# Terraform
export TF_STATE_BUCKET=gb-poc-terraform-state
export TF_STATE_PREFIX=testmazlum
export GOOGLE_PROVIDER_VERSION="= 5.26.0"
```

### Plan the monitoring resources (metric and alerting) with Terraform

```bash
gcloud builds submit \
  --project=$PROJECT_ID \
  --region=$LOCATION \
  --config monitoring-resources-terraform-plan.yaml \
  --substitutions _TF_STATE_BUCKET=$TF_STATE_BUCKET,_TF_STATE_PREFIX=$TF_STATE_PREFIX,_GOOGLE_PROVIDER_VERSION=$GOOGLE_PROVIDER_VERSION \
  --verbosity="debug" .
```

### Apply the monitoring resources with Terraform

```bash
gcloud builds submit \
  --project=$PROJECT_ID \
  --region=$LOCATION \
  --config monitoring-resources-terraform-apply.yaml \
  --substitutions _TF_STATE_BUCKET=$TF_STATE_BUCKET,_TF_STATE_PREFIX=$TF_STATE_PREFIX,_GOOGLE_PROVIDER_VERSION=$GOOGLE_PROVIDER_VERSION \
  --verbosity="debug" .
```

## Deploy the Airflow DAG in Composer with Cloud Build from the local machine

```shell
gcloud builds submit \
    --project=$PROJECT_ID \
    --region=$LOCATION \
    --config deploy-airflow-dag.yaml \
    --substitutions _DAG_FOLDER="$DAG_FOLDER",_COMPOSER_ENVIRONMENT="$COMPOSER_ENVIRONMENT" \
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
    --substitutions _DAG_FOLDER="$DAG_FOLDER",_COMPOSER_ENVIRONMENT="$COMPOSER_ENVIRONMENT",_ENV="$ENV" \
    --verbosity="debug"
```

