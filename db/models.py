from typing import Optional, Literal
from datetime import datetime
from sqlmodel import Field, SQLModel
from enum import Enum


class ApplicationStatus(str, Enum):
    APPLY = "Apply"
    PROCESS = "Process"
    FAILED = "Failed"
    HIRED = "Hired"


class JobApplication(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    link: str = Field(unique=True)
    status: ApplicationStatus = Field(default=ApplicationStatus.APPLY)
    company_name: str
    role : str
    location: str
    salary_min: Optional[int] = None
    description: str
    cv_summary: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
