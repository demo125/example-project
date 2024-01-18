from dagster import Config


class Configs(Config):
    train_split_size: float = 0.8

    model_path: str = "runs:/29c78d43962247c284fef36cb439a2af/model"

    registry_model_name: str = "iris_model"
    registry_model_version: str = "Staging"
    csv_data: str = """
"sepal.length","sepal.width","petal.length","petal.width","variety"
5.1,3.5,1.4,.2,"Setosa"
4.9,3,1.4,.2,"Setosa"
"""
