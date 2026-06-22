from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

# Base schema with shared properties
class JobBase(BaseModel):
    filename: str

# Schema for the full Job response, reflecting the database model
class JobResponse(JobBase):
    id: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    row_count_raw: Optional[int] = None
    row_count_clean: Optional[int] = None
    error_message: Optional[str] = None

    # Allows Pydantic to read data directly from SQLAlchemy model instances
    model_config = ConfigDict(from_attributes=True)

# Schema for just returning the status of a job
class JobStatusResponse(BaseModel):
    id: int
    status: str
    
    model_config = ConfigDict(from_attributes=True)
