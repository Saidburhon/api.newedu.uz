from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, validator
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserType
from app.models.device import App, UserApp, AppRequest
from app.models.enums import GeneralType, AppType, AppRequestStatuses, Priorities

router = APIRouter()


class AppBase(BaseModel):
    """Base schema for app data"""
    name: str
    package_name: str
    general_type: Optional[GeneralType] = None
    app_type: Optional[AppType] = None
    priority: Optional[Priorities] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    @validator('name', 'package_name')
    def validate_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v


class AppResponse(AppBase):
    """Response schema for app"""
    id: int
    created_at: str
    updated_at: str


class AppRequestBase(BaseModel):
    """Base schema for app request"""
    app_id: int
    reason: str
    
    model_config = ConfigDict(from_attributes=True)


@router.get("/", response_model=List[Dict[str, Any]])
async def get_apps(
    general_type: Optional[str] = None,
    app_type: Optional[str] = None,
    priority: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get apps with optional filtering"""
    
    # Start with base query
    query = db.query(App)
    
    # Apply filters if provided
    if general_type:
        try:
            general_type_enum = GeneralType(general_type)
            query = query.filter(App.general_type == general_type_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid general_type: {general_type}"
            )
    
    if app_type:
        try:
            app_type_enum = AppType(app_type)
            query = query.filter(App.app_type == app_type_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid app_type: {app_type}"
            )
    
    if priority:
        try:
            priority_enum = Priorities(priority)
            query = query.filter(App.priority == priority_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid priority: {priority}"
            )
    
    # Execute query
    apps = query.all()
    
    # Format response
    result = []
    for app in apps:
        # Check if user has this app installed
        user_app = db.query(UserApp).filter(
            UserApp.user_id == current_user.id,
            UserApp.app_id == app.id
        ).first()
        
        result.append({
            "id": app.id,
            "name": app.name,
            "package_name": app.package_name,
            "general_type": app.general_type.value if app.general_type else None,
            "app_type": app.app_type.value if app.app_type else None,
            "priority": app.priority.value if app.priority else None,
            "installed": user_app is not None,
            "created_at": app.created_at.isoformat() if app.created_at else None,
            "updated_at": app.updated_at.isoformat() if app.updated_at else None
        })
    
    return result


@router.get("/{app_id}", response_model=Dict[str, Any])
async def get_app(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific app by ID"""
    
    # Get app
    app = db.query(App).filter(App.id == app_id).first()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )
    
    # Check if user has this app installed
    user_app = db.query(UserApp).filter(
        UserApp.user_id == current_user.id,
        UserApp.app_id == app.id
    ).first()
    
    # Return app information
    return {
        "id": app.id,
        "name": app.name,
        "package_name": app.package_name,
        "general_type": app.general_type.value if app.general_type else None,
        "app_type": app.app_type.value if app.app_type else None,
        "priority": app.priority.value if app.priority else None,
        "installed": user_app is not None,
        "created_at": app.created_at.isoformat() if app.created_at else None,
        "updated_at": app.updated_at.isoformat() if app.updated_at else None
    }


@router.post("/installed", response_model=Dict[str, Any])
async def register_installed_app(
    app_data: AppBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register an app as installed on the user's device"""
    
    # Check if app already exists in the database
    existing_app = db.query(App).filter(App.package_name == app_data.package_name).first()
    
    app_id = None
    if existing_app:
        app_id = existing_app.id
    else:
        # Create new app
        new_app = App(
            name=app_data.name,
            package_name=app_data.package_name,
            general_type=app_data.general_type,
            app_type=app_data.app_type,
            priority=app_data.priority
        )
        db.add(new_app)
        db.flush()
        app_id = new_app.id
    
    # Check if user already has this app registered
    existing_user_app = db.query(UserApp).filter(
        UserApp.user_id == current_user.id,
        UserApp.app_id == app_id
    ).first()
    
    if existing_user_app:
        # Update existing record
        existing_user_app.is_active = True
        db.commit()
        
        return {
            "message": "App installation updated",
            "app_id": app_id,
            "user_app_id": existing_user_app.id
        }
    else:
        # Create new user_app record
        try:
            new_user_app = UserApp(
                user_id=current_user.id,
                app_id=app_id,
                is_active=True
            )
            db.add(new_user_app)
            db.commit()
            db.refresh(new_user_app)
            
            return {
                "message": "App installation registered successfully",
                "app_id": app_id,
                "user_app_id": new_user_app.id
            }
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred: {str(e)}"
            )


@router.post("/request", response_model=Dict[str, Any])
async def request_app_approval(
    request_data: AppRequestBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request approval for an app"""
    
    # Check if app exists
    app = db.query(App).filter(App.id == request_data.app_id).first()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found"
        )
    
    # Check if there's already a pending request for this app
    existing_request = db.query(AppRequest).filter(
        AppRequest.user_id == current_user.id,
        AppRequest.app_id == request_data.app_id,
        AppRequest.status == AppRequestStatuses.pending
    ).first()
    
    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A pending request already exists for this app"
        )
    
    # Create new app request
    try:
        new_request = AppRequest(
            user_id=current_user.id,
            app_id=request_data.app_id,
            reason=request_data.reason,
            status=AppRequestStatuses.pending
        )
        db.add(new_request)
        db.commit()
        db.refresh(new_request)
        
        return {
            "message": "App approval request submitted successfully",
            "request_id": new_request.id,
            "app_id": request_data.app_id,
            "app_name": app.name,
            "status": new_request.status.value,
            "created_at": new_request.created_at.isoformat() if new_request.created_at else None
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.get("/requests", response_model=List[Dict[str, Any]])
async def get_app_requests(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get app requests for the current user"""
    
    # Start with base query
    query = db.query(AppRequest).filter(AppRequest.user_id == current_user.id)
    
    # Apply status filter if provided
    if status:
        try:
            status_enum = AppRequestStatuses(status)
            query = query.filter(AppRequest.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}"
            )
    
    # Execute query
    requests = query.all()
    
    # Format response
    result = []
    for req in requests:
        # Get app details
        app = db.query(App).filter(App.id == req.app_id).first()
        
        result.append({
            "id": req.id,
            "app_id": req.app_id,
            "app_name": app.name if app else "Unknown",
            "reason": req.reason,
            "status": req.status.value,
            "created_at": req.created_at.isoformat() if req.created_at else None,
            "updated_at": req.updated_at.isoformat() if req.updated_at else None
        })
    
    return result


@router.get("/types", response_model=Dict[str, Any])
async def get_app_types(current_user: User = Depends(get_current_user)):
    """Get all available app types and general types"""
    
    general_types = {}
    for gen_type in GeneralType:
        general_types[gen_type.name] = gen_type.value
    
    app_types = {}
    for app_type in AppType:
        app_types[app_type.name] = app_type.value
    
    priorities = {}
    for priority in Priorities:
        priorities[priority.name] = priority.value
    
    return {
        "general_types": general_types,
        "app_types": app_types,
        "priorities": priorities
    }


@router.post("/{app_id}/uninstall", response_model=Dict[str, Any])
async def uninstall_app(
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark an app as uninstalled"""
    
    # Check if user has this app installed
    user_app = db.query(UserApp).filter(
        UserApp.user_id == current_user.id,
        UserApp.app_id == app_id
    ).first()
    
    if not user_app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="App not found or not installed"
        )
    
    # Mark as inactive
    user_app.is_active = False
    db.commit()
    
    return {
        "message": "App marked as uninstalled",
        "app_id": app_id
    }
