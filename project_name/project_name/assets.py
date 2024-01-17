import pandas as pd
from dagster import AssetExecutionContext, AssetOut, MarkdownMetadataValue, Out, Output, asset, multi_asset
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, classification_report
from sklearn.tree import DecisionTreeClassifier

from .configs import Configs
from .resources import DVCFileSystemResource
from io import StringIO

@asset(
    description="Fetches data from DVC storage and saves it to local filesystem",
)
def dvc_dataset(
    context: AssetExecutionContext, dvc_fs_resource: DVCFileSystemResource
) -> str:
    dvc_fs = dvc_fs_resource.get_dvc_fs()
    dvc_fs.get("./data", ".", recursive=True)
    dataset_path = "./data/iris.csv"
    return dataset_path

@multi_asset(
    description="Splits dataset into train and test sets",
    outs={
        "train_split": AssetOut(),
        "test_split": AssetOut(),
    }
)
def loaded_dataset(
    context: AssetExecutionContext, dvc_dataset: str
) -> tuple[Output[pd.DataFrame], Output[pd.DataFrame]]:
    df =  pd.read_csv(dvc_dataset)
    train_df, test_df = train_test_split(df, train_size=0.8)
    return Output(train_df, output_name="train_split"), Output(test_df, output_name="test_split") # 
@asset()
def classifier(context: AssetExecutionContext, train_split: pd.DataFrame) -> DecisionTreeClassifier:
    clf = DecisionTreeClassifier()
    clf = clf.fit(train_split[["sepal.length","sepal.width","petal.length","petal.width"]], train_split.variety)
    return clf

@asset()
def eval_classifier(context: AssetExecutionContext, test_split: pd.DataFrame, classifier: DecisionTreeClassifier) -> Output[float]:
    predictions = classifier.predict(test_split[["sepal.length","sepal.width","petal.length","petal.width"]])
    f1: float = f1_score(test_split.variety, predictions, average="micro")
    report = classification_report(test_split.variety, predictions, output_dict=True)
    context.log.info(report)
    return Output(f1, metadata={"report": MarkdownMetadataValue.md(pd.DataFrame(report).transpose().to_markdown())})

@asset()
def predict(context: AssetExecutionContext, classifier: DecisionTreeClassifier, config: Configs) -> Output[list[str]]:
    df = pd.read_csv(StringIO(config.csv_data))
    context.log.info(f"Input data:\n {df}")
    prediction = classifier.predict(df[["sepal.length","sepal.width","petal.length","petal.width"]])
    context.log.info(f"Predicted values: {prediction}")

    return Output(prediction.tolist(), metadata={"prediction": prediction.tolist()})
