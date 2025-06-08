from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserType, StudentInfo, School
from app.schemas.user import StudentInfoUpdate

router = APIRouter()


@router.get("/profile", response_model=Dict[str, Any])
async def get_student_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get student profile details including education information"""
    # Get user type
    user_type = db.query(UserType).filter(UserType.id == current_user.user_type_id).first()
    if not user_type or user_type.name != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only students can access this endpoint."
        )
    
    # Get student-specific information
    student_info = db.query(StudentInfo).filter(StudentInfo.user_id == current_user.id).first()
    if not student_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    # Get school information
    school = None
    if student_info.school:
        school = db.query(School).filter(School.id == student_info.school).first()
    
    return {
        "user": {
            "id": current_user.id,
            "phone_number": current_user.phone_number,
            "username": current_user.username,
            "user_type": user_type.name,
        },
        "student_info": {
            "first_name": student_info.first_name,
            "last_name": student_info.last_name,
            "patronymic": student_info.patronymic,
            "age": student_info.age,
            "gender": student_info.gender.value if student_info.gender else None,
            "shift": student_info.shift.value if student_info.shift else None
        },
        "education": {
            "school_id": student_info.school,
            "school_name": school.name if school else None,
            "school_address": school.address if school else None
        }
    }


@router.put("/update", response_model=Dict[str, Any])
async def update_student_info(student_data: StudentInfoUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update student's information"""
    # Get user type
    user_type = db.query(UserType).filter(UserType.id == current_user.user_type_id).first()
    if not user_type or user_type.name != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only students can access this endpoint."
        )
    
    student_info = db.query(StudentInfo).filter(StudentInfo.user_id == current_user.id).first()
    if not student_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    # Update student data
    update_data = student_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(student_info, key) and value is not None:
            setattr(student_info, key, value)
    
    db.commit()
    db.refresh(student_info)
    
    # Get updated school information
    school = None
    if student_info.school:
        school = db.query(School).filter(School.id == student_info.school).first()
    
    return {
        "message": "Student information updated successfully",
        "student_info": {
            "first_name": student_info.first_name,
            "last_name": student_info.last_name,
            "patronymic": student_info.patronymic,
            "age": student_info.age,
            "gender": student_info.gender.value if student_info.gender else None,
            "shift": student_info.shift.value if student_info.shift else None
        },
        "education": {
            "school_id": student_info.school,
            "school_name": school.name if school else None,
            "school_address": school.address if school else None
        }
    }
