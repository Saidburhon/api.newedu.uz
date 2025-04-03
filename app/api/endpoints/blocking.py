from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, Student

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
    
    class Config:
        from_attributes = True

class EmergencyExceptionRequest(BaseModel):
    package_name: str
    reason: str

# Mock data for demonstration - replace with actual database models later
_mock_blocked_apps = [
    {"id": 1, "package_name": "com.instagram.android", "app_name": "Instagram", "is_blocked": True},
    {"id": 2, "package_name": "com.facebook.katana", "app_name": "Facebook", "is_blocked": True},
    {"id": 3, "package_name": "com.zhiliaoapp.musically", "app_name": "TikTok", "is_blocked": True},
]

# Get current blocking status
@router.get("/status", response_model=dict)
async def get_blocking_status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get the current blocking status for the authenticated student"""
    
    # For now, return mock data based on time and location
    # This would be replaced with actual database lookups in production
    return {
        "blocking_active": True,
        "reason": "School hours (8:00 AM - 2:00 PM)",
        "location_based": True,
        "school_detected": "School №13",
        "current_time": "10:30 AM",
        "is_holiday": False
    }

# Get list of all blocked apps for the current user
@router.get("/rules", response_model=List[BlockedAppResponse])
async def get_blocked_apps(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all apps that are currently blocked for this student"""
    
    # In production, this would be a query to your BlockedApp model
    # For now returning mock data
    return _mock_blocked_apps

# Request emergency exception
@router.post("/emergency-exceptions", status_code=status.HTTP_201_CREATED)
async def request_emergency_exception(
    exception_request: EmergencyExceptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request an emergency exception to unblock a specific app"""
    
    # In production, this would create an EmergencyException record
    # For mock purposes, just return success message
    return {
        "message": "Emergency exception request submitted successfully",
        "status": "pending",
        "estimated_review_time": "within 30 minutes",
        "package_name": exception_request.package_name,
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
    
    # For demonstration, return mock calendar data
    # In production, fetch from your calendar/schedule database
    return {
        "month": month or 4,  # April
        "year": year or 2025,
        "holidays": [
            {"date": "2025-04-21", "name": "Navruz Holiday"},
            {"date": "2025-04-30", "name": "Teacher Development Day"}
        ],
        "special_events": [
            {"date": "2025-04-15", "name": "Science Fair", "blocking_modified": True}
        ]
    }
