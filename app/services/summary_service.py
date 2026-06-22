from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.transaction import Transaction
from app.models.job_summary import JobSummary
from app.services.llm_service import generate_summary_narrative

def generate_job_summary(db: Session, job_id: int) -> JobSummary:
    """
    Generates a JobSummary by aggregating the newly inserted transactions.
    """
    # 1. Total Spend (INR and USD)
    # We query the sum of the amount column, grouped by currency
    spend_by_currency = db.query(
        Transaction.currency, 
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.job_id == job_id
    ).group_by(Transaction.currency).all()
    
    total_spend_inr = 0.0
    total_spend_usd = 0.0
    for currency, total in spend_by_currency:
        if currency and currency.upper() == "INR":
            total_spend_inr = float(total)
        elif currency and currency.upper() == "USD":
            total_spend_usd = float(total)
            
    # 2. Top Merchants
    # Count frequency of transactions per merchant, ordered by count descending
    top_merchants_query = db.query(
        Transaction.merchant,
        func.count(Transaction.id).label('txn_count')
    ).filter(
        Transaction.job_id == job_id
    ).group_by(Transaction.merchant).order_by(desc('txn_count')).limit(3).all()
    
    top_merchants = {merchant: count for merchant, count in top_merchants_query}
    
    # 3. Anomaly Count
    anomaly_count = db.query(func.count(Transaction.id)).filter(
        Transaction.job_id == job_id,
        Transaction.is_anomaly == True
    ).scalar() or 0
    
    # 4. Risk Level and Narrative (Using Gemini)
    risk_level, narrative = generate_summary_narrative(
        total_spend_inr=total_spend_inr,
        total_spend_usd=total_spend_usd,
        top_merchants=top_merchants,
        anomaly_count=anomaly_count
    )
        
    # Create the Summary record
    summary = JobSummary(
        job_id=job_id,
        total_spend_inr=total_spend_inr,
        total_spend_usd=total_spend_usd,
        top_merchants=top_merchants,
        anomaly_count=anomaly_count,
        risk_level=risk_level,
        narrative=narrative
    )
    
    db.add(summary)
    db.commit()
    db.refresh(summary)
    
    return summary
