from pydantic import BaseModel
from typing import List

class TransactionInput(BaseModel):
    description: str
    amount: float

class CategoryPredictionResponse(BaseModel):
    category: str

class AnomalyPredictionResponse(BaseModel):
    is_anomaly: bool

class ForecastResponse(BaseModel):
    dates: List[str]
    predictions: List[float]
