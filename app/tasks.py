import time
from app.core.celery_app import celery_app
from app.db.database import SessionLocal
from app.models.job import Job

@celery_app.task(name="process_csv_task")
def process_csv(job_id: int):
    print(f"Starting to process job_id: {job_id}")
    
    # We must create a new database session because Celery runs in a separate process
    # and cannot share the FastAPI request's database session.
    db = SessionLocal()
    try:
        # 1. Update status to 'processing'
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            print(f"Job {job_id} not found!")
            return
            
        job.status = "processing"
        db.commit()
        
        # 2. Simulate processing work (Wait a few seconds)
        print(f"Processing job {job_id}... (simulated delay)")
        time.sleep(5)
        
        # 3. Update status to 'completed'
        job.status = "completed"
        db.commit()
        print(f"Job {job_id} completed successfully.")
        
    except Exception as e:
        print(f"Error processing job {job_id}: {str(e)}")
        # Rollback any failed transactions and mark job as failed
        db.rollback()
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = "failed"
            job.error_message = str(e)
            db.commit()
    finally:
        # Always close the session to free up the database connection
        db.close()
