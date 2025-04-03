from typing import Optional, Literal

from pydantic import BaseModel, Field, field_validator


class UserBase(BaseModel):
    """Base schema for user data"""
    phone_number: str
    full_name: str

    @field_validator("phone_number", mode='before')
    def validate_phone_number(cls, v):
        # Strip any whitespace
        v = v.strip()
        # Validate Uzbekistan phone number format
        if not v.startswith("+998") or len(v) != 13 or not v[4:].isdigit():
            raise ValueError("Phone number must be in format +998XXXXXXXXX")
        return v


class PhoneNumberCheck(BaseModel):
    """Schema for phone number existence check"""
    phone_number: str
    user_type: Literal["student", "teacher", "admin"]

    @field_validator("phone_number", mode='before')
    def validate_phone_number(cls, v):
        v = v.strip()
        if not v.startswith("+998") or len(v) != 13 or not v[4:].isdigit():
            raise ValueError("Phone number must be in format +998XXXXXXXXX")
        return v


class PhoneNumberCheckResponse(BaseModel):
    """Response schema for phone number check"""
    exists: bool
    message: str


class StudentCreate(UserBase):
    """Schema for creating a student"""
    password: str = Field(..., min_length=6)
    school: str
    grade: int = Field(..., ge=1, le=11)
    class_id: str

    @field_validator("grade")
    def validate_grade(cls, v):
        if v < 1 or v > 11:
            raise ValueError("Grade must be between 1 and 11")
        return v


class TeacherCreate(UserBase):
    """Schema for creating a teacher"""
    password: str = Field(..., min_length=6)
    school: str
    subjects: Optional[str] = None


class AdminCreate(UserBase):
    """Schema for creating an admin"""
    password: str = Field(..., min_length=6)
    role: str = "staff"


class LoginRequest(BaseModel):
    """Schema for login requests"""
    phone_number: str
    password: str
    user_type: Literal["student", "teacher", "admin"]

    @field_validator("phone_number", mode='before')
    def validate_phone_number(cls, v):
        v = v.strip()
        if not v.startswith("+998") or len(v) != 13 or not v[4:].isdigit():
            raise ValueError("Phone number must be in format +998XXXXXXXXX")
        return v


class Token(BaseModel):
    """Schema for auth token response"""
    access_token: str
    token_type: str
    user_id: int
    user_type: str
    expires_at: int  # Unix timestamp


class UserResponse(BaseModel):
    """Schema for user response data"""
    id: int
    phone_number: str
    full_name: str
    user_type: str
    
    class Config:
        from_attributes = True
