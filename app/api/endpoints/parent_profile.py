from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, validator

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserType, ParentInfo
from app.models.enums import Genders

router = APIRouter()


class ParentProfileBase(BaseModel):
    """Base schema for parent profile data"""
    gender: Optional[Genders] = None
    address: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    @validator('address')
    def validate_address(cls, v):
        if v and len(v) > 255:
            raise ValueError('Address must be less than 255 characters')
        return v


class ParentProfileUpdate(ParentProfileBase):
    """Schema for updating parent profile"""
    pass


class ParentProfileResponse(ParentProfileBase):
    """Response schema for parent profile"""
    id: int
    user_id: int
    created_at: str
    updated_at: str


@router.get("/profile", response_model=Dict[str, Any])
async def get_parent_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get the parent profile information for the current user"""
    
    # Check if user is a parent
    user_type = db.query(UserType).filter(UserType.id == current_user.user_type_id).first()
    if not user_type or user_type.name != "parent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only parents can access this endpoint."
        )
    
    # Get parent information
    parent_info = db.query(ParentInfo).filter(ParentInfo.user_id == current_user.id).first()
    if not parent_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent profile not found"
        )
    
    # Return parent profile information
    return {
        "id": parent_info.id,
        "user_id": parent_info.user_id,
        "gender": parent_info.gender.value if parent_info.gender else None,
        "address": parent_info.address,
        "created_at": parent_info.created_at.isoformat() if parent_info.created_at else None,
        "updated_at": parent_info.updated_at.isoformat() if parent_info.updated_at else None
    }


@router.put("/profile", response_model=Dict[str, Any])
async def update_parent_profile(
    profile_data: ParentProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the parent profile information for the current user"""
    
    # Check if user is a parent
    user_type = db.query(UserType).filter(UserType.id == current_user.user_type_id).first()
    if not user_type or user_type.name != "parent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only parents can access this endpoint."
        )
    
    # Get parent information
    parent_info = db.query(ParentInfo).filter(ParentInfo.user_id == current_user.id).first()
    if not parent_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent profile not found"
        )
    
    # Update parent information
    if profile_data.gender is not None:
        parent_info.gender = profile_data.gender
    if profile_data.address is not None:
        parent_info.address = profile_data.address
    
    try:
        db.commit()
        db.refresh(parent_info)
        
        return {
            "message": "Parent profile updated successfully",
            "id": parent_info.id,
            "user_id": parent_info.user_id,
            "gender": parent_info.gender.value if parent_info.gender else None,
            "address": parent_info.address,
            "created_at": parent_info.created_at.isoformat() if parent_info.created_at else None,
            "updated_at": parent_info.updated_at.isoformat() if parent_info.updated_at else None
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.get("/children", response_model=Dict[str, Any])
async def get_parent_children(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get the children associated with the current parent user"""
    
    # Check if user is a parent
    user_type = db.query(UserType).filter(UserType.id == current_user.user_type_id).first()
    if not user_type or user_type.name != "parent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only parents can access this endpoint."
        )
    
    # Get parent information
    parent_info = db.query(ParentInfo).filter(ParentInfo.user_id == current_user.id).first()
    if not parent_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent profile not found"
        )
    
    # For now, return a mock response
    # In a real implementation, we would query for children associated with this parent
    return {
        "message": "This endpoint will return children associated with the parent",
        "parent_id": parent_info.id,
        "children": [
            # Mock data - in real implementation, this would be actual children data
            {
                "id": 1,
                "name": "Child 1",
                "age": 10,
                "school": "School 1"
            },
            {
                "id": 2,
                "name": "Child 2",
                "age": 8,
                "school": "School 2"
            }
        ]
    }
