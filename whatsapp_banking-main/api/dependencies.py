from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.models import get_db
from services.auth_services import check_authentication

def verify_authentication():
    """Verify that the service is authenticated"""
    if not check_authentication():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed. Service is currently unavailable."
        )
    return True

def get_db_session(db: Session = Depends(get_db)):
    """Get database session"""
    return db
