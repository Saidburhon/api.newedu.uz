from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, StudentInfo, ParentInfo
from app.models.preferences import UserPreference
from app.schemas.user import UserResponse, StudentInfoResponse, ParentInfoResponse, UserPreferenceResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information"""
    return current_user


@router.get("/me/student-info", response_model=StudentInfoResponse)
async def read_student_info(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get student information for the current user"""
    student_info = db.query(StudentInfo).filter(StudentInfo.user_id == current_user.id).first()
    if not student_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student information not found for this user"
        )
    return student_info


@router.get("/me/parent-info", response_model=ParentInfoResponse)
async def read_parent_info(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get parent information for the current user"""
    parent_info = db.query(ParentInfo).filter(ParentInfo.user_id == current_user.id).first()
    if not parent_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent information not found for this user"
        )
    return parent_info


@router.get("/me/preferences", response_model=UserPreferenceResponse)
async def read_user_preferences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get preferences for the current user"""
    preferences = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found for this user"
        )
    return preferences
