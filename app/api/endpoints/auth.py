from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.schemas.user import LoginRequest, Token, PhoneNumberCheck, PhoneNumberCheckResponse

router = APIRouter()


@router.post("/check-phone", response_model=PhoneNumberCheckResponse)
async def check_phone_number(data: PhoneNumberCheck, db: Session = Depends(get_db)):
    """Check if a phone number exists for the given user type"""
    user = db.query(User).filter(
        User.phone_number == data.phone_number,
        User.user_type == data.user_type
    ).first()

    if user:
        return {
            "exists": True,
            "message": "User exists. Please proceed to login."
        }
    else:
        return {
            "exists": False,
            "message": "User not found. Please register."
        }


@router.post("/login", response_model=Token)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Login endpoint that returns a JWT token"""
    user = db.query(User).filter(
        User.phone_number == data.phone_number,
        User.user_type == data.user_type
    ).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, expires_at = create_access_token(
        data={"sub": user.id, "type": user.user_type}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "user_type": user.user_type,
        "expires_at": expires_at
    }
