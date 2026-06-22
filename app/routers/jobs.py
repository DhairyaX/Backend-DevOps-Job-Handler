from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.job import Job
from app.schemas.job import JobResponse, JobStatusResponse
from app.services.job_service import create_job_and_save_file

# Create a router specifically for /jobs endpoints
router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/upload", response_model=JobResponse)
def upload_job(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a CSV file, save it to disk, and create a pending Job record.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    # Use our service function to handle DB and file operations
    job = create_job_and_save_file(db, file)
    return job

@router.get("", response_model=List[JobResponse])
def get_all_jobs(db: Session = Depends(get_db)):
    """
    Retrieve all jobs from the database.
    """
    jobs = db.query(Job).all()
    return jobs

@router.get("/{job_id}/status", response_model=JobStatusResponse)
def get_job_status(job_id: int, db: Session = Depends(get_db)):
    """
    Get the current status of a specific job by its ID.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job

@router.get("/{job_id}/results")
def get_job_results(job_id: int, db: Session = Depends(get_db)):
    """
    Get the final results of a specific job. (Placeholder for now)
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return {
        "message": "Results processing is not yet implemented",
        "job_id": job_id,
        "status": job.status
    }
