from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
from app.core.security import hash_password, create_access_token, settings
from app.core.database import get_db
from app.models.user import User, UserType, StudentInfo, ParentInfo
from app.schemas.user import UserCreate, StudentInfoCreate, ParentInfoCreate, UserPreferenceCreate
from app.models.preferences import UserPreference

router = APIRouter()


@router.post("/user", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if phone number already exists for this user type
    existing_user = db.query(User).filter(
        User.phone_number == user_data.phone_number,
        User.user_type_id == user_data.user_type_id
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered for this user type"
        )

    try:
        # Create new user
        new_user = User(
            phone_number=user_data.phone_number,
            username=user_data.username,
            user_type_id=user_data.user_type_id,
            password_hash=hash_password(user_data.password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Generate access token
        access_token_data = {
            "sub": str(new_user.id),
            "phone": new_user.phone_number,
            "user_type_id": new_user.user_type_id
        }
        token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token, token_expiry = create_access_token(access_token_data, expires_delta=token_expires)

        return {
            "message": "User registered successfully",
            "user_id": new_user.id,
            "access_token": access_token,
            "token_type": "bearer",
            "expires_at": token_expiry
        }
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed due to database constraint: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.post("/student-info", status_code=status.HTTP_201_CREATED)
async def create_student_info(student_data: StudentInfoCreate, db: Session = Depends(get_db)):
    """Create student information for an existing user"""
    # Check if user exists
    user = db.query(User).filter(User.id == student_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if student info already exists for this user
    existing_info = db.query(StudentInfo).filter(StudentInfo.user_id == student_data.user_id).first()
    if existing_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student information already exists for this user"
        )

    try:
        # Create student info
        new_student_info = StudentInfo(
            user_id=student_data.user_id,
            first_name=student_data.first_name,
            last_name=student_data.last_name,
            patronymic=student_data.patronymic,
            age=student_data.age,
            gender=student_data.gender,
            school=student_data.school,
            shift=student_data.shift,
            father=student_data.father,
            mother=student_data.mother
        )
        db.add(new_student_info)
        db.commit()
        db.refresh(new_student_info)

        return {
            "message": "Student information created successfully",
            "id": new_student_info.id
        }
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Creation failed due to database constraint: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.post("/parent-info", status_code=status.HTTP_201_CREATED)
async def create_parent_info(parent_data: ParentInfoCreate, db: Session = Depends(get_db)):
    """Create parent information for an existing user"""
    # Check if user exists
    user = db.query(User).filter(User.id == parent_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if parent info already exists for this user
    existing_info = db.query(ParentInfo).filter(ParentInfo.user_id == parent_data.user_id).first()
    if existing_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parent information already exists for this user"
        )

    try:
        # Create parent info
        new_parent_info = ParentInfo(
            user_id=parent_data.user_id,
            first_name=parent_data.first_name,
            last_name=parent_data.last_name,
            patronymic=parent_data.patronymic,
            age=parent_data.age,
            gender=parent_data.gender,
            passport_id=parent_data.passport_id
        )
        db.add(new_parent_info)
        db.commit()
        db.refresh(new_parent_info)

        return {
            "message": "Parent information created successfully",
            "id": new_parent_info.id
        }
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Creation failed due to database constraint: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.post("/preferences", status_code=status.HTTP_201_CREATED)
async def create_user_preferences(pref_data: UserPreferenceCreate, db: Session = Depends(get_db)):
    """Create user preferences for an existing user"""
    # Check if user exists
    user = db.query(User).filter(User.id == pref_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if preferences already exist for this user
    existing_prefs = db.query(UserPreference).filter(UserPreference.user_id == pref_data.user_id).first()
    if existing_prefs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Preferences already exist for this user"
        )

    try:
        # Create user preferences
        new_preferences = UserPreference(
            user_id=pref_data.user_id,
            language=pref_data.language,
            theme=pref_data.theme
        )
        db.add(new_preferences)
        db.commit()
        db.refresh(new_preferences)

        return {
            "message": "User preferences created successfully",
            "id": new_preferences.id
        }
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Creation failed due to database constraint: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
