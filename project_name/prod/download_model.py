import os

import mlflow
from dotenv import load_dotenv

load_dotenv()

# a bug ?
os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("MLFLOW_S3_AWS_ACCESS_KEY_ID")
os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("MLFLOW_S3_AWS_SECRET_ACCESS_KEY")

model_uri = f"models:/iris_model/production"
model = mlflow.sklearn.load_model(model_uri)

mlflow.sklearn.save_model(model, "model")
