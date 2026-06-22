import os
import pandas as pd
from app.core.celery_app import celery_app
from app.db.database import SessionLocal
from app.models.job import Job
from app.models.transaction import Transaction

UPLOAD_DIR = "uploads"

@celery_app.task(name="process_csv_task")
def process_csv(job_id: int):
    print(f"Starting to process job_id: {job_id}")
    db = SessionLocal()
    try:
        # 1. Fetch Job and update status
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            print(f"Job {job_id} not found!")
            return
            
        job.status = "processing"
        db.commit()
        
        # 2. Read the CSV using pandas
        file_path = os.path.join(UPLOAD_DIR, f"{job.id}_{job.filename}")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found")
            
        df = pd.read_csv(file_path)
        row_count_raw = len(df)
        job.row_count_raw = row_count_raw
        
        # 3. Data Cleaning
        
        # Remove exact duplicate rows
        df = df.drop_duplicates()
        
        # Normalize dates to ISO format (YYYY-MM-DD)
        if 'date' in df.columns:
            # handle formats like 04-09-2024 and 2024/02/05
            df['date'] = pd.to_datetime(df['date'], format='mixed', dayfirst=True).dt.date
            
        # Remove currency symbols from amount and convert to float
        if 'amount' in df.columns:
            # Keep only digits, minus signs, and decimals
            df['amount'] = df['amount'].astype(str).str.replace(r'[^\d.-]', '', regex=True)
            # Handle empty strings resulting from regex
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            
        # Uppercase status values
        if 'status' in df.columns:
            df['status'] = df['status'].astype(str).str.upper()
            
        # Fill missing categories with "Uncategorised"
        if 'category' in df.columns:
            df['category'] = df['category'].fillna("Uncategorised")
            # Also replace empty strings
            df.loc[df['category'] == '', 'category'] = "Uncategorised"
            
        # Drop columns that are not in our database model
        expected_columns = ['txn_id', 'date', 'merchant', 'amount', 'currency', 'status', 'category', 'account_id']
        df = df[[col for col in expected_columns if col in df.columns]]
        
        row_count_clean = len(df)
        job.row_count_clean = row_count_clean
        
        # 4. Store cleaned transactions in the database
        # Convert DataFrame to a list of dictionaries
        records = df.to_dict(orient='records')
        
        # Add job_id to each record
        for record in records:
            record['job_id'] = job.id
            
            # Ensure NaN values are handled (e.g. if amount couldn't be parsed)
            if pd.isna(record.get('amount')):
                record['amount'] = 0.0
                
        # Bulk insert
        db.bulk_insert_mappings(Transaction, records)
        
        # 5. Update job status to completed
        job.status = "completed"
        db.commit()
        print(f"Job {job_id} completed successfully. Raw: {row_count_raw}, Clean: {row_count_clean}")
        
    except Exception as e:
        print(f"Error processing job {job_id}: {str(e)}")
        db.rollback()
        # Ensure we try to re-fetch the job in case the session state is bad
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = "failed"
            job.error_message = str(e)
            db.commit()
    finally:
        db.close()
