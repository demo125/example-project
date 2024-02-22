import pandas as pd
from evidently import ColumnMapping
from evidently.metric_preset import ClassificationPreset
from evidently.report import Report
from evidently.test_preset import DataQualityTestPreset
from evidently.test_suite import TestSuite

data = pd.read_csv("./data/iris.csv")


def get_column_mapping() -> ColumnMapping:
    target = "variety"
    prediction = "prediction"
    numerical_features = [
        "sepal.length",
        "sepal.width",
        "petal.length",
        "petal.width",
    ]
    column_mapping = ColumnMapping()

    column_mapping.target = target
    column_mapping.prediction = target
    column_mapping.numerical_features = numerical_features
    column_mapping.categorical_features = []
    return column_mapping


def get_classification_report(
    current_data: pd.DataFrame, reference_data: pd.DataFrame | None = None
) -> Report:

    classification_report = Report(
        metrics=[
            ClassificationPreset(),
        ],
    )
    classification_report.run(
        current_data=current_data,
        reference_data=current_data,
        column_mapping=get_column_mapping(),
    )

    return classification_report


def get_data_quality_test(
    current_data: pd.DataFrame, reference_data: pd.DataFrame | None = None
) -> Report:

    data_quality_test_suite = TestSuite(tests=[DataQualityTestPreset()])
    data_quality_test_suite.run(
        reference_data=reference_data,
        current_data=current_data,
        column_mapping=get_column_mapping(),
    )
    return data_quality_test_suite
