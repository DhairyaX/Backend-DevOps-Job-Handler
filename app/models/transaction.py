from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey
from app.db.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))  # Foreign key linking to the jobs table
    txn_id = Column(String, index=True)
    date = Column(Date)
    merchant = Column(String)
    amount = Column(Float)
    currency = Column(String)
    status = Column(String)
    category = Column(String)
    account_id = Column(String)
    
    # Fields updated by the AI (LLM) Processing
    is_anomaly = Column(Boolean, default=False)
    anomaly_reason = Column(String, nullable=True)
    llm_category = Column(String, nullable=True)
    llm_raw_response = Column(String, nullable=True)
    llm_failed = Column(Boolean, default=False)
