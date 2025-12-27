from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
import pandas as pd
import io
from fastapi.responses import StreamingResponse
import csv
from io import StringIO
from sqlalchemy.orm import Session
import hashlib
from backend.db.models import UploadedFile
from backend.db.database import get_db
from backend.db.models import Transaction
from backend.ml import model_loader
from datetime import date
from typing import Optional
router = APIRouter(prefix="/transactions", tags=["Transactions"])

REQUIRED_COLUMNS = {
    "date",
    "description",
    "amount",
    "transaction_type",
    "account_name"
}

@router.post("/upload")
async def upload_transactions(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)   # DB injected
):

    # ---------- File validation ----------
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a CSV file."
        )

    contents = await file.read()
    file_hash = hashlib.sha256(contents).hexdigest()

    # ---------- DUPLICATE CHECK ----------
    existing_file = (
        db.query(UploadedFile)
        .filter(UploadedFile.file_hash == file_hash)
        .first()
    )

    if existing_file:
        raise HTTPException(
            status_code=409,
            detail="This file has already been uploaded."
        )
    # ---------- Read CSV ----------

    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error reading CSV file: {e}"
        )

    # ---------- Normalize columns ----------
    df.columns = (
        df.columns
        .str.lower()
        .str.replace(" ", "_")
    )

    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns: {missing_columns}"
        )

    # ---------- Parse date ----------
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    # ---------- ML Predictions ----------
    X_cat = df[["description", "amount"]]
    df["predicted_category"] = model_loader.category_model.predict(X_cat)

    df["is_anomaly"] = (
        model_loader.anomaly_model.predict(df[["amount"]]) == -1
    )

    # ---------- SAVE TO DATABASE ----------
    for _, row in df.iterrows():
        tx = Transaction(
            date=row["date"].date(),   # store as DATE
            description=row["description"],
            amount=float(row["amount"]),
            transaction_type=row["transaction_type"],
            account_name=row["account_name"],
            predicted_category=row["predicted_category"],
            is_anomaly=bool(row["is_anomaly"])
        )
        db.add(tx)

    db.commit()   # COMMIT ONCE

    # ---------- SAVE FILE HASH  ----------
    uploaded = UploadedFile(file_hash=file_hash)
    db.add(uploaded)
    db.commit()

    # ---------- Category Aggregation ----------
    category_summary = (
        df.groupby("predicted_category")["amount"]
        .sum()
        .sort_values(ascending=False)
    )

    # ---------- Anomaly Aggregation ----------
    anomaly_count = df["is_anomaly"].value_counts().to_dict()

    # ---------- Monthly Spending ----------
    monthly_spending = (
        df[df["amount"] > 0]
        .set_index("date")
        .resample("M")["amount"]
        .sum()
    )
    monthly_spending.index = monthly_spending.index.strftime("%Y-%m")

    # ---------- API Response ----------
    response = {
        "total_transactions": len(df),
        "anomalies_detected": int(df["is_anomaly"].sum()),
        "category_summary": category_summary.to_dict(),
        "anomaly_summary": {
            "normal": anomaly_count.get(False, 0),
            "anomaly": anomaly_count.get(True, 0)
        },
        "monthly_spending": monthly_spending.to_dict(),
        "data": df.to_dict(orient="records"),
        "preview": df.head(20).to_dict(orient="records")
    }

    return response
@router.get("/")
def get_transactions(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[str] = None,
    account: Optional[str] = None,
    anomaly: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Transaction)

    if start_date:
        query = query.filter(Transaction.date >= start_date)

    if end_date:
        query = query.filter(Transaction.date <= end_date)

    if category:
        query = query.filter(Transaction.predicted_category == category)

    if account:
        query = query.filter(Transaction.account_name == account)

    if anomaly is not None:
        query = query.filter(Transaction.is_anomaly == anomaly)

    total = query.count()

    results = (
        query
        .order_by(Transaction.date.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    return {
        "total": total,
        "data": results
    }

@router.get("/export")
def export_transactions(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[str] = None,
    account: Optional[str] = None,
    anomaly: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Transaction)

    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    if category:
        query = query.filter(Transaction.predicted_category == category)
    if account:
        query = query.filter(Transaction.account_name == account)
    if anomaly is not None:
        query = query.filter(Transaction.is_anomaly == anomaly)

    results = query.order_by(Transaction.date.desc()).all()

    def generate_csv():
        buffer = StringIO()
        writer = csv.writer(buffer)

        # Header
        writer.writerow([
            "date",
            "description",
            "amount",
            "transaction_type",
            "account_name",
            "predicted_category",
            "is_anomaly"
        ])

        for tx in results:
            writer.writerow([
                tx.date,
                tx.description,
                tx.amount,
                tx.transaction_type,
                tx.account_name,
                tx.predicted_category,
                tx.is_anomaly
            ])

        buffer.seek(0)
        return buffer

    return StreamingResponse(
        generate_csv(),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=transactions_export.csv"
        }
    )
@router.get("/filters")
def get_filter_values(db: Session = Depends(get_db)):
    categories = [
        r[0] for r in
        db.query(Transaction.predicted_category).distinct().all()
    ]

    accounts = [
        r[0] for r in
        db.query(Transaction.account_name).distinct().all()
    ]

    return {
        "categories": categories,
        "accounts": accounts
    }
