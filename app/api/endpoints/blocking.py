from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserType, StudentInfo, School, App
from app.models.device import UserApp
from app.models.enums import AppRequestStatuses

router = APIRouter()

# Schema models for the blocking functionality
class BlockedAppBase(BaseModel):
    package_name: str
    app_name: str

class BlockedAppCreate(BlockedAppBase):
    pass

class BlockedAppResponse(BlockedAppBase):
    id: int
    is_blocked: bool
    
    model_config = ConfigDict(from_attributes=True)

class EmergencyExceptionRequest(BaseModel):
    app_id: int
    reason: str

# Get current blocking status
@router.get("/status", response_model=Dict[str, Any])
async def get_blocking_status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get the current blocking status for the authenticated student"""
    
    # Check if user is a student
    user_type = db.query(UserType).filter(UserType.id == current_user.user_type_id).first()
    if not user_type or user_type.name != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only students can access this endpoint."
        )
    
    # Get student information
    student_info = db.query(StudentInfo).filter(StudentInfo.user_id == current_user.id).first()
    if not student_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    # Get school information
    school = None
    school_name = "Unknown"
    if student_info.school:
        school = db.query(School).filter(School.id == student_info.school).first()
        if school:
            school_name = school.name
    
    # For now, return mock data based on time and location
    # This would be replaced with actual database lookups in production
    current_time = datetime.now()
    return {
        "blocking_active": True,
        "reason": "School hours (8:00 AM - 2:00 PM)",
        "location_based": True,
        "school_detected": school_name,
        "current_time": current_time.strftime("%H:%M"),
        "is_holiday": False,
        "shift": student_info.shift.value if student_info.shift else None
    }

# Get list of all blocked apps for the current user
@router.get("/blocked-apps", response_model=List[Dict[str, Any]])
async def get_blocked_apps(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all apps that are currently blocked for this student"""
    
    # Check if user is a student
    user_type = db.query(UserType).filter(UserType.id == current_user.user_type_id).first()
    if not user_type or user_type.name != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only students can access this endpoint."
        )
    
    # In a real implementation, we would query the database for blocked apps
    # For now, we'll return a combination of real apps from the database and mock blocking status
    apps = db.query(App).limit(10).all()
    
    blocked_apps = []
    for app in apps:
        # Check if user has this app installed
        user_app = db.query(UserApp).filter(
            UserApp.user_id == current_user.id,
            UserApp.app_id == app.id
        ).first()
        
        # For demo purposes, block social media apps
        is_blocked = False
        if app.general_type and app.general_type.value == "Social":
            is_blocked = True
        
        blocked_apps.append({
            "id": app.id,
            "package_name": app.package_name,
            "app_name": app.name,
            "is_blocked": is_blocked,
            "installed": user_app is not None,
            "category": app.general_type.value if app.general_type else "Unknown"
        })
    
    return blocked_apps

# Request emergency exception
@router.post("/emergency-exceptions", status_code=status.HTTP_201_CREATED)
async def request_emergency_exception(
    exception_request: EmergencyExceptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request an emergency exception to unblock a specific app"""
    
    # Check if user is a student
    user_type = db.query(UserType).filter(UserType.id == current_user.user_type_id).first()
    if not user_type or user_type.name != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only students can access this endpoint."
        )
    
    # Check if app exists
    app = db.query(App).filter(App.id == exception_request.app_id).first()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )
    
    # In production, this would create an AppRequest record
    # For mock purposes, just return success message
    return {
        "message": "Emergency exception request submitted successfully",
        "status": AppRequestStatuses.pending.value,
        "estimated_review_time": "within 30 minutes",
        "app_id": exception_request.app_id,
        "app_name": app.name,
        "reason": exception_request.reason
    }

# Get school schedule (holidays, special events)
@router.get("/school-schedule")
async def get_school_schedule(
    month: Optional[int] = None,
    year: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get school schedule including holidays and special events"""
    
    # Check if user is a student
    user_type = db.query(UserType).filter(UserType.id == current_user.user_type_id).first()
    if not user_type or user_type.name != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only students can access this endpoint."
        )
    
    # Get student information
    student_info = db.query(StudentInfo).filter(StudentInfo.user_id == current_user.id).first()
    if not student_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    # Get current date if not provided
    now = datetime.now()
    if not month:
        month = now.month
    if not year:
        year = now.year
    
    # For demonstration, return mock calendar data
    # In production, fetch from your calendar/schedule database
    return {
        "month": month,
        "year": year,
        "school_id": student_info.school,
        "shift": student_info.shift.value if student_info.shift else None,
        "holidays": [
            {"date": f"{year}-{month:02d}-21", "name": "Navruz Holiday"},
            {"date": f"{year}-{month:02d}-30", "name": "Teacher Development Day"}
        ],
        "special_events": [
            {"date": f"{year}-{month:02d}-15", "name": "Science Fair", "blocking_modified": True}
        ]
    }
