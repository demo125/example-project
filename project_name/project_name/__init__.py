
from dagster import Definitions
from dotenv import load_dotenv
from .assets import (
    dvc_dataset, loaded_dataset, classifier, eval_classifier, predict
    )
from .resources import DVCFileSystemResource

# dagster loads .env file automatically, loading env manualy is needed for pytest test autodiscovery
load_dotenv()


from dagster import AssetSelection, define_asset_job

defs = Definitions(
    assets=[dvc_dataset, loaded_dataset, classifier, eval_classifier, predict],
    # jobs=[my_job],
    # jobs=[fetch_chastia_metadata, store_tables_to_parquet, store_tables_to_lake],
    # sensors=[fetch_chastia_metadata_job_sensor, detect_chastia_parquet_job_sensor],
    resources={
        "dvc_fs_resource": DVCFileSystemResource(),
        # "minio": MinioResource(
        #     endpoint_url=os.environ["SOURCE_TO_LAKE_MINIO_ENDPOINT_URL"],
        #     aws_key_id=os.environ["SOURCE_TO_LAKE_MINIO_AWS_KEY_ID"],
        #     aws_secret_key=os.environ["SOURCE_TO_LAKE_MINIO_AWS_SECRET_KEY"],
        #     bucket=os.environ["SOURCE_TO_LAKE_CHASTIA_MINIO_BUCKET"],
        # ),
    },
)
