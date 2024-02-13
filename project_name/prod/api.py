import csv
import os

import mlflow
import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

# Define where to save predictions
PREDICTIONS_CSV = "./predictions/predictions.csv"

# Define the FastAPI app
app = FastAPI()
# Load the trained machine learning model
model = mlflow.sklearn.load_model("./model")


# Define a Pydantic model for input validation
class IrisInput(BaseModel):
    sepal_length: float = Field(serialization_alias="sepal.length")
    sepal_width: float = Field(serialization_alias="sepal.width")
    petal_length: float = Field(serialization_alias="petal.length")
    petal_width: float = Field(serialization_alias="petal.width")


class IrisRow(IrisInput):
    prediction: str = Field(alias="prediction")


def save_to_csv(row: IrisRow):

    file_exists = os.path.isfile(PREDICTIONS_CSV)
    data = row.model_dump(by_alias=True)
    columns = list(data.keys())

    with open(PREDICTIONS_CSV, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(columns)
        writer.writerow([data[c] for c in columns])


# Define endpoint for making predictions
@app.get("/prediction-data")
async def data():
    df = pd.read_csv(PREDICTIONS_CSV)
    return df.to_csv()


@app.post("/predict")
async def predict(data: IrisInput):
    # Extract features from input
    features = np.array(
        [[data.sepal_length, data.sepal_width, data.petal_length, data.petal_width]]
    )

    # Make prediction
    prediction = model.predict(features)[0]

    # save to file
    iris_row = IrisRow(
        sepal_length=data.sepal_length,
        sepal_width=data.sepal_width,
        petal_length=data.petal_length,
        petal_width=data.petal_width,
        prediction=prediction,
    )

    save_to_csv(iris_row)

    return {"prediction": prediction}
