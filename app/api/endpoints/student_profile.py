from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, Student
from app.schemas.user import UserResponse

router = APIRouter()


@router.get("/profile", response_model=dict)
async def get_student_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get student profile details including education information"""
    if current_user.user_type != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only students can access this endpoint."
        )
    
    # Get student-specific information
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    return {
        "user": {
            "id": current_user.id,
            "phone_number": current_user.phone_number,
            "full_name": current_user.full_name,
            "user_type": current_user.user_type,
        },
        "education": {
            "school": student.school,
            "grade": student.grade,
            "class_id": student.class_id
        }
    }


@router.put("/update-school", response_model=dict)
async def update_school_info(school_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update student's school information"""
    if current_user.user_type != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only students can access this endpoint."
        )
    
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    # Update student data
    if "school" in school_data:
        student.school = school_data["school"]
    if "grade" in school_data:
        student.grade = school_data["grade"]
    if "class_id" in school_data:
        student.class_id = school_data["class_id"]
    
    db.commit()
    db.refresh(student)
    
    return {
        "message": "School information updated successfully",
        "education": {
            "school": student.school,
            "grade": student.grade,
            "class_id": student.class_id
        }
    }
