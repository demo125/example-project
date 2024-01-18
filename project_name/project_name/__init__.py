import os

from dagster import AssetSelection, Definitions, define_asset_job
from dagster_mlflow import mlflow_tracking
from dotenv import load_dotenv

# from .jobs import train_model
from .assets import (
    classifier,
    dvc_dataset,
    eval_classifier,
    loaded_dataset,
    model_predict_from_path,
    model_predict_from_registry,
    predict,
)
from .resources import DVCFileSystemResource

# dagster loads .env file automatically, loading env manualy is needed for pytest test autodiscovery
load_dotenv()

import git

repo = git.Repo(search_parent_directories=True)
sha = repo.head.object.hexsha

mlflow_resoruce = mlflow_tracking.configured(
    {
        "experiment_name": "exmple-project",
        "mlflow_tracking_uri": os.getenv("MLFLOW_TRACKING_URI"),
        # env variables to pass to mlflow
        "env": {
            "MLFLOW_TRACKING_INSECURE_TLS": os.getenv("MLFLOW_TRACKING_INSECURE_TLS"),
            # s3
            "MLFLOW_S3_ENDPOINT_URL": os.getenv("MLFLOW_S3_ENDPOINT_URL"),
            "MLFLOW_S3_IGNORE_TLS": os.getenv("MLFLOW_S3_IGNORE_TLS"),
            "AWS_ACCESS_KEY_ID": os.getenv("MLFLOW_S3_AWS_ACCESS_KEY_ID"),
            "AWS_SECRET_ACCESS_KEY": os.getenv("MLFLOW_S3_AWS_SECRET_ACCESS_KEY"),
        },
        # env variables you want to log as mlflow tags
        # "env_to_tag": ["DOCKER_IMAGE_TAG"],
        # key-value tags to add to your experiment
        "extra_tags": {"git_commit_sha": sha},
    }
)

training_asset_job = define_asset_job(
    name="train_model", selection=AssetSelection.groups("training")
)
prediction_asset_job = define_asset_job(
    name="prediction", selection=AssetSelection.groups("prediction")
)

defs = Definitions(
    assets=[
        dvc_dataset,
        loaded_dataset,
        classifier,
        eval_classifier,
        predict,
        model_predict_from_registry,
        model_predict_from_path,
    ],
    jobs=[training_asset_job, prediction_asset_job],
    # jobs=[fetch_chastia_metadata, store_tables_to_parquet, store_tables_to_lake],
    # sensors=[fetch_chastia_metadata_job_sensor, detect_chastia_parquet_job_sensor],
    resources={
        "dvc_fs_resource": DVCFileSystemResource(),
        "mlflow": mlflow_resoruce
        # "minio": MinioResource(
        #     endpoint_url=os.environ["SOURCE_TO_LAKE_MINIO_ENDPOINT_URL"],
        #     aws_key_id=os.environ["SOURCE_TO_LAKE_MINIO_AWS_KEY_ID"],
        #     aws_secret_key=os.environ["SOURCE_TO_LAKE_MINIO_AWS_SECRET_KEY"],
        #     bucket=os.environ["SOURCE_TO_LAKE_CHASTIA_MINIO_BUCKET"],
        # ),
    },
)
