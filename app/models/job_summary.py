from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.types import JSON
from app.db.database import Base

class JobSummary(Base):
    __tablename__ = "job_summaries"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), unique=True) # One-to-one relationship with a job
    total_spend_inr = Column(Float, default=0.0)
    total_spend_usd = Column(Float, default=0.0)
    top_merchants = Column(JSON)  # Stores JSON data representing top merchants
    anomaly_count = Column(Integer, default=0)
    narrative = Column(String, nullable=True)
    risk_level = Column(String, nullable=True)
