from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserType, App
from app.models.device import Log, Action, Device, UserDevice
from app.models.enums import ActionDegrees

router = APIRouter()


class LogBase(BaseModel):
    """Base schema for log data"""
    device_id: int
    app_id: Optional[int] = None
    action_id: int
    duration: Optional[int] = None  # Duration in seconds
    
    model_config = ConfigDict(from_attributes=True)


class LogCreate(LogBase):
    """Schema for creating a log entry"""
    pass


class LogResponse(LogBase):
    """Response schema for log"""
    id: int
    user_id: int
    created_at: str


@router.post("/", response_model=Dict[str, Any])
async def create_log(
    log_data: LogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new log entry"""
    
    # Verify device belongs to user
    user_device = db.query(UserDevice).filter(
        UserDevice.user_id == current_user.id,
        UserDevice.device_id == log_data.device_id
    ).first()
    
    if not user_device:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Device does not belong to user"
        )
    
    # Verify action exists
    action = db.query(Action).filter(Action.id == log_data.action_id).first()
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found"
        )
    
    # Verify app exists if provided
    if log_data.app_id:
        app = db.query(App).filter(App.id == log_data.app_id).first()
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="App not found"
            )
    
    # Create log entry
    try:
        new_log = Log(
            user_id=current_user.id,
            device_id=log_data.device_id,
            app_id=log_data.app_id,
            action_id=log_data.action_id,
            duration=log_data.duration
        )
        
        db.add(new_log)
        db.commit()
        db.refresh(new_log)
        
        return {
            "message": "Log entry created successfully",
            "id": new_log.id,
            "user_id": new_log.user_id,
            "device_id": new_log.device_id,
            "app_id": new_log.app_id,
            "action_id": new_log.action_id,
            "duration": new_log.duration,
            "created_at": new_log.created_at.isoformat() if new_log.created_at else None
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.get("/", response_model=List[Dict[str, Any]])
async def get_logs(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    device_id: Optional[int] = None,
    app_id: Optional[int] = None,
    action_degree: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get logs with optional filtering"""
    
    # Check if user is a parent or admin to view logs
    user_type = db.query(UserType).filter(UserType.id == current_user.user_type_id).first()
    if not user_type or (user_type.name != "parent" and user_type.name != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only parents and admins can view logs."
        )
    
    # Start with base query
    query = db.query(Log)
    
    # If user is a parent, only show logs for their children
    # For now, we'll just filter by the current user's ID
    # In a real implementation, we would query for children associated with this parent
    if user_type.name == "parent":
        query = query.filter(Log.user_id == current_user.id)
    
    # Apply filters if provided
    if start_date:
        try:
            start_datetime = datetime.fromisoformat(start_date)
            query = query.filter(Log.created_at >= start_datetime)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid start_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
            )
    
    if end_date:
        try:
            end_datetime = datetime.fromisoformat(end_date)
            query = query.filter(Log.created_at <= end_datetime)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
            )
    
    if device_id:
        query = query.filter(Log.device_id == device_id)
    
    if app_id:
        query = query.filter(Log.app_id == app_id)
    
    if action_degree:
        try:
            degree_enum = ActionDegrees(action_degree)
            # Join with Action to filter by degree
            query = query.join(Action).filter(Action.degree == degree_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid action_degree: {action_degree}"
            )
    
    # Execute query with limit
    logs = query.order_by(Log.created_at.desc()).limit(100).all()
    
    # Format response
    result = []
    for log in logs:
        # Get related information
        device = db.query(Device).filter(Device.id == log.device_id).first()
        app = None
        if log.app_id:
            app = db.query(App).filter(App.id == log.app_id).first()
        action = db.query(Action).filter(Action.id == log.action_id).first()
        
        result.append({
            "id": log.id,
            "user_id": log.user_id,
            "device": {
                "id": device.id if device else None,
                "name": device.device_name if device else "Unknown"
            },
            "app": {
                "id": app.id if app else None,
                "name": app.name if app else None,
                "package_name": app.package_name if app else None
            } if log.app_id else None,
            "action": {
                "id": action.id if action else None,
                "name": action.name if action else "Unknown",
                "degree": action.degree.value if action and action.degree else None
            },
            "duration": log.duration,
            "created_at": log.created_at.isoformat() if log.created_at else None
        })
    
    return result


@router.get("/actions", response_model=List[Dict[str, Any]])
async def get_actions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all available actions"""
    
    actions = db.query(Action).all()
    
    result = []
    for action in actions:
        result.append({
            "id": action.id,
            "name": action.name,
            "degree": action.degree.value if action.degree else None
        })
    
    return result


@router.get("/summary", response_model=Dict[str, Any])
async def get_log_summary(
    days: Optional[int] = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a summary of logs for the specified number of days"""
    
    # Check if user is a parent or admin to view logs
    user_type = db.query(UserType).filter(UserType.id == current_user.user_type_id).first()
    if not user_type or (user_type.name != "parent" and user_type.name != "admin" and user_type.name != "student"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only students, parents and admins can view log summaries."
        )
    
    # Calculate start date
    start_date = datetime.now() - timedelta(days=days)
    
    # Get user ID to filter logs
    user_id = current_user.id
    
    # If user is a parent, we would get their children's IDs
    # For now, we'll just use the current user's ID
    
    # Get total logs count
    total_logs = db.query(Log).filter(
        Log.user_id == user_id,
        Log.created_at >= start_date
    ).count()
    
    # Get logs by action degree
    suspicious_logs = db.query(Log).join(Action).filter(
        Log.user_id == user_id,
        Log.created_at >= start_date,
        Action.degree == ActionDegrees.suspicious
    ).count()
    
    terrible_logs = db.query(Log).join(Action).filter(
        Log.user_id == user_id,
        Log.created_at >= start_date,
        Action.degree == ActionDegrees.terrible
    ).count()
    
    # Get top apps by usage
    top_apps_query = db.query(
        App.id, App.name, App.package_name, 
        db.func.count(Log.id).label('usage_count'),
        db.func.sum(Log.duration).label('total_duration')
    ).join(Log, Log.app_id == App.id).filter(
        Log.user_id == user_id,
        Log.created_at >= start_date,
        Log.app_id.isnot(None)
    ).group_by(App.id).order_by(db.func.count(Log.id).desc()).limit(5)
    
    top_apps = []
    for app_id, name, package_name, usage_count, total_duration in top_apps_query:
        top_apps.append({
            "id": app_id,
            "name": name,
            "package_name": package_name,
            "usage_count": usage_count,
            "total_duration": total_duration or 0  # Handle None values
        })
    
    return {
        "period_days": days,
        "start_date": start_date.isoformat(),
        "end_date": datetime.now().isoformat(),
        "total_logs": total_logs,
        "suspicious_logs": suspicious_logs,
        "terrible_logs": terrible_logs,
        "top_apps": top_apps
    }
