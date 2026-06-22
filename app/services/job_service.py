import os
import shutil
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.job import Job

# Define the directory where uploads will be saved
UPLOAD_DIR = "uploads"
# Create the directory if it doesn't already exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

def create_job_and_save_file(db: Session, file: UploadFile) -> Job:
    # 1. Create a new Job record in the PostgreSQL database
    new_job = Job(
        filename=file.filename,
        status="pending"
    )
    db.add(new_job)
    db.commit() # Save the job to the database
    db.refresh(new_job) # Reload the job to get the auto-generated ID from Postgres

    # 2. Save the uploaded file to the local disk
    # We prefix the filename with the job ID to prevent naming conflicts
    file_path = os.path.join(UPLOAD_DIR, f"{new_job.id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return new_job
