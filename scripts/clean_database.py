#!/usr/bin/env python
"""
Script to clean all job applications from the database.
This can be used for maintenance, testing, or resetting the database.
"""
import os
import sys

# Add the project root directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.crud import delete_all_job_applications
from db.models import JobApplication
from db.database import engine
from sqlmodel import Session, select


def main():
    # First show count of current records
    with Session(engine) as session:
        statement = select(JobApplication)
        current_count = len(list(session.exec(statement)))
        print(f"Current job application count: {current_count}")
    
    # Ask for confirmation
    if current_count > 0:
        confirmation = input(f"Are you sure you want to delete all {current_count} job applications? (yes/no): ")
        if confirmation.lower() != "yes":
            print("Operation cancelled.")
            return
    
        # Proceed with deletion
        delete_all_job_applications(session=session)
        
        # Verify deletion
        with Session(engine) as session:
            final_count = len(list(session.exec(select(JobApplication))))
            print(f"Final job application count: {final_count}")
            
            if final_count == 0:
                print("Database successfully cleaned!")
            else:
                print(f"Warning: {final_count} records still remain.")
    else:
        print("Database is already empty. Nothing to clean.")


if __name__ == "__main__":
    main()
