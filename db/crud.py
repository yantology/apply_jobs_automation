from sqlmodel import Session, select
from typing import Optional, List
from .models import JobApplication, ApplicationStatus


def create_job_application(session: Session, job_application: JobApplication) -> JobApplication:
    """
    Create a new job application entry in the database.
    
    Args:
        session: The database session
        job_application: The JobApplication object to add
        
    Returns:
        The created JobApplication with ID
    """
    session.add(job_application)
    session.commit()
    session.refresh(job_application)
    return job_application


def check_link_availability(session: Session, link: str) -> bool:
    """
    Check if a job application link is available (i.e., not already in the database).
    
    Args:
        session: The database session
        link: The unique link to check
        
    Returns:
        True if the link is not found (available), False if it already exists.
    """
    statement = select(JobApplication.id).where(JobApplication.link == link) # Select only ID for efficiency
    existing_application = session.exec(statement).first()
    return existing_application is None


def get_job_by_link(session: Session, link: str) -> Optional[JobApplication]:
    """
    Find a job application by its link.
    
    Args:
        session: The database session
        link: The unique link to search for
        
    Returns:
        The JobApplication if found, None otherwise
    """
    statement = select(JobApplication).where(JobApplication.link == link)
    return session.exec(statement).first()


def get_all_job_applications(session: Session) -> List[JobApplication]:
    """
    Get all job applications.
    
    Args:
        session: The database session
    
    Returns:
        List of all JobApplication objects
    """
    statement = select(JobApplication)
    return list(session.exec(statement))


def update_job_application_status(session: Session, job_id: int, status: ApplicationStatus) -> Optional[JobApplication]:
    """
    Update the status of a job application.
    
    Args:
        session: The database session
        job_id: The ID of the job application to update
        status: The new status
        
    Returns:
        The updated JobApplication if found, None otherwise
    """
    job = session.get(JobApplication, job_id)
    if job:
        job.status = status
        session.add(job)
        session.commit()
        session.refresh(job)
    return job


def delete_all_job_applications(session: Session) -> int:
    """
    Delete all job applications from the database.
    
    Args:
        session: The database session
    
    Returns:
        Number of records deleted
    """
    statement = select(JobApplication)
    applications = list(session.exec(statement))
    count = len(applications)
    
    # Delete all records
    for application in applications:
        session.delete(application)
    
    session.commit()
    return count
