from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.core.security import hash_password
from app.models.user import User, Student, Teacher, Admin
from app.schemas.user import StudentCreate, TeacherCreate, AdminCreate

router = APIRouter()


@router.post("/student", status_code=status.HTTP_201_CREATED)
async def register_student(student_data: StudentCreate, db: Session = Depends(get_db)):
    """Register a new student"""
    # Check if phone number already exists
    existing_user = db.query(User).filter(User.phone_number == student_data.phone_number).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )

    try:
        # Create new user
        new_user = User(
            phone_number=student_data.phone_number,
            full_name=student_data.full_name,
            password_hash=hash_password(student_data.password),
            user_type="student"
        )
        db.add(new_user)
        db.flush()  # Flush to get the user ID

        # Create student profile
        new_student = Student(
            user_id=new_user.id,
            school=student_data.school,
            grade=student_data.grade,
            class_id=student_data.class_id
        )
        db.add(new_student)
        db.commit()

        return {"message": "Student registered successfully", "user_id": new_user.id}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed. Please try again."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.post("/teacher", status_code=status.HTTP_201_CREATED)
async def register_teacher(teacher_data: TeacherCreate, db: Session = Depends(get_db)):
    """Register a new teacher"""
    # Check if phone number already exists
    existing_user = db.query(User).filter(User.phone_number == teacher_data.phone_number).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )

    try:
        # Create new user
        new_user = User(
            phone_number=teacher_data.phone_number,
            full_name=teacher_data.full_name,
            password_hash=hash_password(teacher_data.password),
            user_type="teacher"
        )
        db.add(new_user)
        db.flush()  # Flush to get the user ID

        # Create teacher profile
        new_teacher = Teacher(
            user_id=new_user.id,
            school=teacher_data.school,
            subjects=teacher_data.subjects
        )
        db.add(new_teacher)
        db.commit()

        return {"message": "Teacher registered successfully", "user_id": new_user.id}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed. Please try again."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.post("/admin", status_code=status.HTTP_201_CREATED)
async def register_admin(admin_data: AdminCreate, db: Session = Depends(get_db)):
    """Register a new administrator"""
    # Check if phone number already exists
    existing_user = db.query(User).filter(User.phone_number == admin_data.phone_number).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )

    try:
        # Create new user
        new_user = User(
            phone_number=admin_data.phone_number,
            full_name=admin_data.full_name,
            password_hash=hash_password(admin_data.password),
            user_type="admin"
        )
        db.add(new_user)
        db.flush()  # Flush to get the user ID

        # Create admin profile
        new_admin = Admin(
            user_id=new_user.id,
            role=admin_data.role
        )
        db.add(new_admin)
        db.commit()

        return {"message": "Admin registered successfully", "user_id": new_user.id}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed. Please try again."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
