# Job Application Tracking System Database Documentation

This document provides detailed information about the database design, schema, and operations for the Job Application Tracking System.

## Technology Stack

- **Database**: SQLite
- **ORM**: SQLModel (combines SQLAlchemy Core and Pydantic)
- **Migration Tool**: Alembic
- **Package Management**: uv

## Database Schema

### JobApplication Table

The main table for storing job application data.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique identifier for each job application |
| link | String | Unique | URL of the job posting |
| status | Enum | Not Null | Current status of the application (Apply, Process, Failed, Hired) |
| company_name | String | Not Null | Name of the company |
| location | String | Not Null | Location of the job |
| salary_min | Integer | Nullable | Minimum salary for the position |
| description | String | Not Null | Description of the job position |
| cv_summary | String | Not Null | Summary of the CV submitted for this application |
| created_at | DateTime | Not Null | Timestamp when the record was created |
| updated_at | DateTime | Not Null | Timestamp when the record was last updated |

### ApplicationStatus Enum

Defines the possible states for a job application:

- **Apply**: Initial application submitted
- **Process**: Application is being processed/interviewed
- **Failed**: Application was rejected
- **Hired**: Successfully hired for the position

## Database Setup

The database is set up using SQLModel and Alembic for migrations. The database is stored in a SQLite file named `job_applications.db` in the project root directory.

### Initial Setup

1. The database models are defined in `db/models.py`
2. Database connection configuration is in `db/database.py`
3. Alembic is configured for managing database migrations

## Database Migrations

Alembic is used for tracking and applying database schema changes.

### Migration Commands

To create a new migration:

```bash
uv run alembic revision --autogenerate -m "Description of changes"
```

To apply all pending migrations:

```bash
uv run alembic upgrade head
```

To roll back the last migration:

```bash
uv run alembic downgrade -1
```

### Migration History

1. Initial migration: Created the JobApplication table with all required columns

## Database Operations

The system provides several functions for interacting with the database:

### Adding a Job Application

```python
from job_operations import add_job_application

add_job_application(
    link="https://example.com/job-posting",
    company_name="Company Name",
    location="Job Location",
    description="Job Description",
    cv_summary="CV Summary Text",
    salary_min=100000,  # Optional
)
```

### Finding a Job Application by Link

```python
from job_operations import find_by_link_standalone

job = find_by_link_standalone("https://example.com/job-posting")
if job:
    print(f"Found: {job.company_name}")
```

### Updating Job Application Status

```python
from job_operations import update_status
from db.models import ApplicationStatus

update_status(job_id=1, new_status=ApplicationStatus.PROCESS)
```

### Listing All Job Applications

```python
from job_operations import list_all_applications

list_all_applications()
```

## Command Line Interface

The system provides a simple CLI for interacting with the job applications database:

### Add a Job Application

```bash
uv run python job_operations.py add "https://example.com/job" "Company Name" "Location" "Job Description" "CV Summary" 100000
```

### Find a Job Application by Link

```bash
uv run python job_operations.py find "https://example.com/job"
```

### Update Job Application Status

```bash
uv run python job_operations.py update 1 Process
```

### List All Job Applications

```bash
uv run python job_operations.py list
```

## Demo Script

The system includes a demonstration script (`demo_job_tracking.py`) that showcases its functionality by:

1. Initializing the database (creating tables if they don't exist).
2. Adding several example job applications.
3. Attempting to add a job application with a duplicate link to demonstrate uniqueness handling.
4. Listing all applications.
5. Finding a specific application by link.
6. Attempting to find a non-existent application by link.
7. Updating the status of an application.
8. Displaying the final list with the updated status.

Run the demo script with:

```bash
uv run python demo_job_tracking.py
```

## Database Maintenance

For optimal performance:

1. **Regular Backups**: Create backups of the SQLite database file
2. **Indexing**: The system currently uses indexes on the primary key and `link` column (unique constraint)
3. **Cleanup**: Consider implementing a cleanup process for old or rejected applications
