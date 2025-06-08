from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, validator, HttpUrl

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserType
from app.models.device import Website, Policy
from app.models.enums import GeneralType, Priorities

router = APIRouter()


class WebsiteBase(BaseModel):
    """Base schema for website data"""
    url: str
    name: str
    general_type: Optional[GeneralType] = None
    priority: Optional[Priorities] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    @validator('url')
    def validate_url(cls, v):
        if not v or not v.strip():
            raise ValueError('URL cannot be empty')
        # Basic URL validation - in a real app, you might want more sophisticated validation
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v


class WebsiteResponse(WebsiteBase):
    """Response schema for website"""
    id: int
    created_at: str
    updated_at: str


class PolicyBase(BaseModel):
    """Base schema for policy data"""
    title: str
    content: str
    version: str
    
    model_config = ConfigDict(from_attributes=True)
    
    @validator('title', 'content', 'version')
    def validate_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v


class PolicyResponse(PolicyBase):
    """Response schema for policy"""
    id: int
    created_at: str
    updated_at: str


@router.get("/", response_model=List[Dict[str, Any]])
async def get_websites(
    general_type: Optional[str] = None,
    priority: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get websites with optional filtering"""
    
    # Start with base query
    query = db.query(Website)
    
    # Apply filters if provided
    if general_type:
        try:
            general_type_enum = GeneralType(general_type)
            query = query.filter(Website.general_type == general_type_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid general_type: {general_type}"
            )
    
    if priority:
        try:
            priority_enum = Priorities(priority)
            query = query.filter(Website.priority == priority_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid priority: {priority}"
            )
    
    # Execute query
    websites = query.all()
    
    # Format response
    result = []
    for website in websites:
        result.append({
            "id": website.id,
            "url": website.url,
            "name": website.name,
            "general_type": website.general_type.value if website.general_type else None,
            "priority": website.priority.value if website.priority else None,
            "created_at": website.created_at.isoformat() if website.created_at else None,
            "updated_at": website.updated_at.isoformat() if website.updated_at else None
        })
    
    return result


@router.get("/{website_id}", response_model=Dict[str, Any])
async def get_website(
    website_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific website by ID"""
    
    # Get website
    website = db.query(Website).filter(Website.id == website_id).first()
    
    if not website:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Website not found"
        )
    
    # Return website information
    return {
        "id": website.id,
        "url": website.url,
        "name": website.name,
        "general_type": website.general_type.value if website.general_type else None,
        "priority": website.priority.value if website.priority else None,
        "created_at": website.created_at.isoformat() if website.created_at else None,
        "updated_at": website.updated_at.isoformat() if website.updated_at else None
    }


@router.post("/", response_model=Dict[str, Any])
async def create_website(
    website_data: WebsiteBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new website (admin only)"""
    
    # Check if user is an admin
    user_type = db.query(UserType).filter(UserType.id == current_user.user_type_id).first()
    if not user_type or user_type.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only admins can create websites."
        )
    
    # Check if website with same URL already exists
    existing_website = db.query(Website).filter(Website.url == website_data.url).first()
    if existing_website:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Website with this URL already exists"
        )
    
    # Create new website
    try:
        new_website = Website(
            url=website_data.url,
            name=website_data.name,
            general_type=website_data.general_type,
            priority=website_data.priority
        )
        
        db.add(new_website)
        db.commit()
        db.refresh(new_website)
        
        return {
            "message": "Website created successfully",
            "id": new_website.id,
            "url": new_website.url,
            "name": new_website.name,
            "general_type": new_website.general_type.value if new_website.general_type else None,
            "priority": new_website.priority.value if new_website.priority else None,
            "created_at": new_website.created_at.isoformat() if new_website.created_at else None
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.get("/policies", response_model=List[Dict[str, Any]])
async def get_policies(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all policies"""
    
    policies = db.query(Policy).all()
    
    result = []
    for policy in policies:
        result.append({
            "id": policy.id,
            "title": policy.title,
            "content": policy.content,
            "version": policy.version,
            "created_at": policy.created_at.isoformat() if policy.created_at else None,
            "updated_at": policy.updated_at.isoformat() if policy.updated_at else None
        })
    
    return result


@router.get("/policies/{policy_id}", response_model=Dict[str, Any])
async def get_policy(
    policy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific policy by ID"""
    
    # Get policy
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    # Return policy information
    return {
        "id": policy.id,
        "title": policy.title,
        "content": policy.content,
        "version": policy.version,
        "created_at": policy.created_at.isoformat() if policy.created_at else None,
        "updated_at": policy.updated_at.isoformat() if policy.updated_at else None
    }


@router.post("/policies", response_model=Dict[str, Any])
async def create_policy(
    policy_data: PolicyBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new policy (admin only)"""
    
    # Check if user is an admin
    user_type = db.query(UserType).filter(UserType.id == current_user.user_type_id).first()
    if not user_type or user_type.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only admins can create policies."
        )
    
    # Create new policy
    try:
        new_policy = Policy(
            title=policy_data.title,
            content=policy_data.content,
            version=policy_data.version
        )
        
        db.add(new_policy)
        db.commit()
        db.refresh(new_policy)
        
        return {
            "message": "Policy created successfully",
            "id": new_policy.id,
            "title": new_policy.title,
            "version": new_policy.version,
            "created_at": new_policy.created_at.isoformat() if new_policy.created_at else None
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.get("/latest-policy", response_model=Dict[str, Any])
async def get_latest_policy(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get the latest policy"""
    
    # Get the latest policy by created_at date
    latest_policy = db.query(Policy).order_by(Policy.created_at.desc()).first()
    
    if not latest_policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No policies found"
        )
    
    # Return policy information
    return {
        "id": latest_policy.id,
        "title": latest_policy.title,
        "content": latest_policy.content,
        "version": latest_policy.version,
        "created_at": latest_policy.created_at.isoformat() if latest_policy.created_at else None,
        "updated_at": latest_policy.updated_at.isoformat() if latest_policy.updated_at else None
    }
