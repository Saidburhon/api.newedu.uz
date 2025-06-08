from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel, ConfigDict

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.preferences import UserPreference
from app.models.enums import Languages, Themes

router = APIRouter()


class UserPreferencesBase(BaseModel):
    """Base schema for user preferences"""
    language: Optional[Languages] = None
    theme: Optional[Themes] = None
    notifications_enabled: Optional[bool] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserPreferencesUpdate(UserPreferencesBase):
    """Schema for updating user preferences"""
    pass


class UserPreferencesResponse(UserPreferencesBase):
    """Response schema for user preferences"""
    id: int
    user_id: int
    created_at: str
    updated_at: str


@router.get("/", response_model=Dict[str, Any])
async def get_user_preferences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get the preferences for the current user"""
    
    # Get user preferences
    user_preferences = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    
    if not user_preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found"
        )
    
    # Return user preferences
    return {
        "id": user_preferences.id,
        "user_id": user_preferences.user_id,
        "language": user_preferences.language.value if user_preferences.language else None,
        "theme": user_preferences.theme.value if user_preferences.theme else None,
        "notifications_enabled": user_preferences.notifications_enabled,
        "created_at": user_preferences.created_at.isoformat() if user_preferences.created_at else None,
        "updated_at": user_preferences.updated_at.isoformat() if user_preferences.updated_at else None
    }


@router.put("/", response_model=Dict[str, Any])
async def update_user_preferences(
    preferences_data: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the preferences for the current user"""
    
    # Get user preferences
    user_preferences = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    
    if not user_preferences:
        # Create preferences if they don't exist
        user_preferences = UserPreference(user_id=current_user.id)
        db.add(user_preferences)
    
    # Update preferences
    if preferences_data.language is not None:
        user_preferences.language = preferences_data.language
    if preferences_data.theme is not None:
        user_preferences.theme = preferences_data.theme
    if preferences_data.notifications_enabled is not None:
        user_preferences.notifications_enabled = preferences_data.notifications_enabled
    
    try:
        db.commit()
        db.refresh(user_preferences)
        
        return {
            "message": "User preferences updated successfully",
            "id": user_preferences.id,
            "user_id": user_preferences.user_id,
            "language": user_preferences.language.value if user_preferences.language else None,
            "theme": user_preferences.theme.value if user_preferences.theme else None,
            "notifications_enabled": user_preferences.notifications_enabled,
            "created_at": user_preferences.created_at.isoformat() if user_preferences.created_at else None,
            "updated_at": user_preferences.updated_at.isoformat() if user_preferences.updated_at else None
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.get("/available-languages", response_model=Dict[str, Any])
async def get_available_languages(current_user: User = Depends(get_current_user)):
    """Get all available language options"""
    
    languages = {}
    for lang in Languages:
        languages[lang.name] = lang.value
    
    return {
        "languages": languages
    }


@router.get("/available-themes", response_model=Dict[str, Any])
async def get_available_themes(current_user: User = Depends(get_current_user)):
    """Get all available theme options"""
    
    themes = {}
    for theme in Themes:
        themes[theme.name] = theme.value
    
    return {
        "themes": themes
    }
