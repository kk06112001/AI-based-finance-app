from fastapi import APIRouter
import pandas as pd

from backend.ml import model_loader
from backend.schemas.request_response import (
    TransactionInput,
    CategoryPredictionResponse,
    AnomalyPredictionResponse,
    ForecastResponse
)

router = APIRouter(prefix="/predict", tags=["Predictions"])


@router.post("/category", response_model=CategoryPredictionResponse)
def predict_category(transaction: TransactionInput):
    X = pd.DataFrame([{
        "description": transaction.description,
        "amount": transaction.amount
    }])

    prediction = model_loader.category_model.predict(X)[0]
    return {"category": prediction}


@router.post("/anomaly", response_model=AnomalyPredictionResponse)
def predict_anomaly(transaction: TransactionInput):
    X = [[transaction.amount]]
    pred = model_loader.anomaly_model.predict(X)[0]

    is_anomaly = True if pred == -1 else False
    return {"is_anomaly": is_anomaly}


@router.get("/forecast", response_model=ForecastResponse)
def predict_forecast():
    future = model_loader.forecast_model.make_future_dataframe(periods=3, freq="M")
    forecast = model_loader.forecast_model.predict(future)

    result = forecast.tail(3)

    return {
        "dates": result["ds"].astype(str).tolist(),
        "predictions": result["yhat"].tolist()
    }
