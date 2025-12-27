from fastapi import APIRouter, Depends, HTTPException
from backend.ml.forecast import forecast_monthly_spending

router = APIRouter(prefix="/forecast", tags=["Forecast"])

@router.post("/monthly")
async def monthly_forecast(payload: dict):
    if "monthly_spending" not in payload:
        raise HTTPException(status_code=400, detail="Missing 'monthly_spending' in payload")
    
    forecast=forecast_monthly_spending(
        payload["monthly_spending"],
    )

    return {"forecast": forecast}
