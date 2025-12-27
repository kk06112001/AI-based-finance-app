from fastapi import FastAPI
from backend.routers import predict,transactions,forecast
from fastapi.middleware.cors import CORSMiddleware
from backend.ml.model_loader import load_models

app=FastAPI(title="Financial Transactions Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
def startup_event():
    load_models()

app.include_router(predict.router)
app.include_router(transactions.router)
app.include_router(forecast.router)
@app.get("/")
def root():
    return {"status": "Welcome to the Financial Transactions Prediction API"}