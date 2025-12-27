import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../../"))

CATEGORY_MODEL_PATH = os.path.join(PROJECT_ROOT, "ml/artifacts/category_model.joblib")
ANOMALY_MODEL_PATH = os.path.join(PROJECT_ROOT, "ml/artifacts/anomaly_model.joblib")
FORECAST_MODEL_PATH = os.path.join(PROJECT_ROOT, "ml/artifacts/forecast_model.joblib")

category_model = None
anomaly_model = None
forecast_model = None

def load_models():
    global category_model, anomaly_model, forecast_model

    category_model = joblib.load(CATEGORY_MODEL_PATH)
    anomaly_model = joblib.load(ANOMALY_MODEL_PATH)
    forecast_model = joblib.load(FORECAST_MODEL_PATH)

    print("models loaded successfully")
