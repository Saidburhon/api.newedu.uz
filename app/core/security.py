from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def hash_password(password: str) -> str:
    """Hash a password for storing"""
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    """Verify a stored password against a provided password"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a new access token"""
    to_encode = data.copy()
    
    # Ensure 'sub' is a string 
    if 'sub' in to_encode and not isinstance(to_encode['sub'], str):
        to_encode['sub'] = str(to_encode['sub'])
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt, int(expire.timestamp())


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get the current user from the token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        print(f"Token received: {token[:15]}...")
        print(f"Using secret key: {settings.SECRET_KEY[:5]}...")
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            print(f"Decoded payload: {payload}")
            
            # Extract user_id from 'sub' claim (now as string)
            user_id_str = payload.get("sub")
            user_type = payload.get("type")
            
            if user_id_str is None or user_type is None:
                print("Missing user_id or user_type in payload")
                raise credentials_exception
            
            # Convert user_id from string to integer
            try:
                user_id = int(user_id_str)
            except (ValueError, TypeError):
                print(f"Invalid user_id format: {user_id_str}")
                raise credentials_exception
                
        except jwt.PyJWTError as e:
            print(f"JWT decode error: {str(e)}")
            # Try to decode without verification to see what's inside
            try:
                decoded = jwt.decode(token, options={"verify_signature": False})
                print(f"Token content (not verified): {decoded}")
            except Exception as inner_e:
                print(f"Cannot decode token content: {str(inner_e)}")
            raise credentials_exception
            
    except Exception as e:
        print(f"General exception: {str(e)}")
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or user.user_type != user_type:
        print(f"User not found or user_type mismatch: {user_type}")
        raise credentials_exception
        
    return user
