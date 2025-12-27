from sqlalchemy import Column, Integer, String, Float,Date, Boolean, DateTime
from .database import Base
from datetime import datetime
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date=Column(Date, index=True)
    description = Column(String)
    amount = Column(Float)
    transaction_type = Column(String)  
    account_name = Column(String)
    predicted_category = Column(String)
    is_anomaly = Column(Boolean)


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    file_hash = Column(String, unique=True, index=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)   