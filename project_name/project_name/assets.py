from io import StringIO

import flatdict
import pandas as pd
from dagster import (
    AssetExecutionContext,
    AssetOut,
    ConfigurableResource,
    MarkdownMetadataValue,
    Output,
    asset,
    multi_asset,
)
from evidently.ui.base import Project
from evidently.ui.workspace import Workspace
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from .configs import Configs
from .evidently_ai import get_classification_report, get_data_quality_test
from .resources import DVCFileSystemResource


@asset(
    description="Fetches data from DVC storage and saves it to local filesystem",
    group_name="training",
)
def dvc_dataset(
    context: AssetExecutionContext,
    dvc_fs_resource: DVCFileSystemResource,
    mlflow: ConfigurableResource,
) -> pd.DataFrame:
    dvc_fs = dvc_fs_resource.get_dvc_fs()
    dvc_fs.get("./data", ".", recursive=True)
    dataset_path = "./data/iris.csv"
    mlflow.log_param("dataset_path", dataset_path)
    df = pd.read_csv(dataset_path)
    return df


@multi_asset(
    description="Splits dataset into train and test sets",
    group_name="training",
    outs={
        "train_split": AssetOut(),
        "test_split": AssetOut(),
    },
)
def loaded_dataset(
    context: AssetExecutionContext,
    dvc_dataset: pd.DataFrame,
    config: Configs,
    mlflow: ConfigurableResource,
) -> tuple[Output[pd.DataFrame], Output[pd.DataFrame]]:
    train_df, test_df = train_test_split(
        dvc_dataset, train_size=config.train_split_size
    )
    mlflow.log_param("train_split_size", config.train_split_size)
    return Output(train_df, output_name="train_split"), Output(
        test_df, output_name="test_split"
    )  #


@asset(group_name="training")
def classifier(
    context: AssetExecutionContext,
    train_split: pd.DataFrame,
    mlflow: ConfigurableResource,
) -> DecisionTreeClassifier:
    clf = DecisionTreeClassifier()
    clf = clf.fit(
        train_split[["sepal.length", "sepal.width", "petal.length", "petal.width"]],
        train_split.variety,
    )
    mlflow.sklearn.log_model(clf, artifact_path="model")
    return clf


@asset(group_name="training")
def eval_classifier(
    context: AssetExecutionContext,
    test_split: pd.DataFrame,
    classifier: DecisionTreeClassifier,
    mlflow: ConfigurableResource,
) -> Output[float]:
    predictions = classifier.predict(
        test_split[["sepal.length", "sepal.width", "petal.length", "petal.width"]]
    )
    f1: float = f1_score(test_split.variety, predictions, average="micro")
    report = classification_report(test_split.variety, predictions, output_dict=True)
    context.log.info(report)
    mlflow.log_metrics(flatdict.FlatDict(report, delimiter="_"))
    return Output(
        f1,
        metadata={
            "report": MarkdownMetadataValue.md(
                pd.DataFrame(report).transpose().to_markdown()
            )
        },
    )


def predict_model(
    context: AssetExecutionContext, classifier: DecisionTreeClassifier, csv_data: str
) -> Output[list[str]]:
    df = pd.read_csv(StringIO(csv_data))
    context.log.info(f"Input data:\n {df}")

    prediction = classifier.predict(
        df[["sepal.length", "sepal.width", "petal.length", "petal.width"]]
    )
    context.log.info(f"Predicted values: {prediction}")

    return Output(prediction.tolist(), metadata={"prediction": prediction.tolist()})


@asset(group_name="training")
def predict(
    context: AssetExecutionContext, classifier: DecisionTreeClassifier, config: Configs
) -> Output[list[str]]:
    return predict_model(
        context=context, classifier=classifier, csv_data=config.csv_data
    )


@asset(group_name="prediction")
def model_predict_from_registry(
    context: AssetExecutionContext, config: Configs, mlflow: ConfigurableResource
) -> Output[list[str]]:
    classifier = mlflow.sklearn.load_model(
        model_uri=f"models:/{config.registry_model_name}/{config.registry_model_version}"
    )
    return predict_model(
        context=context, classifier=classifier, csv_data=config.csv_data
    )


@asset(group_name="prediction")
def model_predict_from_path(
    context: AssetExecutionContext, config: Configs, mlflow: ConfigurableResource
) -> Output[list[str]]:
    classifier = mlflow.sklearn.load_model(config.run_model_path)
    return predict_model(
        context=context, classifier=classifier, csv_data=config.csv_data
    )


@multi_asset(
    description="Creates or fetches evidently ai project and workspace",
    group_name="evidently_report",
    outs={
        "evidently_ai_iris_project": AssetOut(),
        "evidently_ai_iris_workspace": AssetOut(),
    },
)
def evidently_ai(
    context: AssetExecutionContext,
) -> tuple[Output[Project], Output[Workspace]]:

    workspace = Workspace.create("./data/evidently")
    projects = {p.name: p for p in workspace.list_projects()}
    if "iris" not in projects:
        project = workspace.create_project("iris")
    else:
        project = projects["iris"]

    return (
        Output(project, output_name="evidently_ai_iris_project"),
        Output(workspace, output_name="evidently_ai_iris_workspace"),
    )


@asset(group_name="evidently_report")
def classification_report(
    context: AssetExecutionContext,
    evidently_ai_iris_project: Project,
    evidently_ai_iris_workspace: Workspace,
    test_split: pd.DataFrame,
    classifier: DecisionTreeClassifier,
) -> str:

    test_predictions = classifier.predict(
        test_split[["sepal.length", "sepal.width", "petal.length", "petal.width"]]
    )
    test_split["predictions"] = test_predictions
    classification_report = get_classification_report(
        current_data=test_split, reference_data=None
    )
    html = classification_report.get_html()
    classification_report.save_json("./data/classification_report.json")
    classification_report.save_html("./data/classification_report.html")

    evidently_ai_iris_workspace.add_report(
        project_id=evidently_ai_iris_project.id, report=classification_report
    )

    return html


@asset(group_name="evidently_report")
def datadrift_report(
    context: AssetExecutionContext,
    train_split: pd.DataFrame,
    evidently_ai_iris_project: Project,
    evidently_ai_iris_workspace: Workspace,
) -> str:

    data_quality_report = get_data_quality_test(
        current_data=train_split, reference_data=None
    )
    html = data_quality_report.get_html()
    data_quality_report.save_json("./data/data_quality_report.json")
    data_quality_report.save_html("./data/data_quality_report.html")

    evidently_ai_iris_workspace.add_report(
        project_id=evidently_ai_iris_project.id, report=data_quality_report
    )

    return html


# @asset(group_name="evidently_report")
# def model_predict_from_path(
#     context: AssetExecutionContext, config: Configs, mlflow: ConfigurableResource
# ) -> Output[list[str]]:
#     classifier = mlflow.sklearn.load_model(config.run_model_path)
#     return predict_model(
#         context=context, classifier=classifier, csv_data=config.csv_data
#     )
