from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.models.enums import (
    Priorities, Genders, Shifts, Languages, Themes,
    AppRequestStatuses, UserRole
)


class UserTypeBase(BaseModel):
    """Base schema for user type data"""
    name: str
    user_level: Optional[int] = None
    school: Optional[int] = None


class UserTypeCreate(UserTypeBase):
    """Schema for creating a user type"""
    pass


class UserTypeResponse(UserTypeBase):
    """Response schema for user type"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    """Base schema for user data"""
    phone_number: str
    username: Optional[str] = None
    user_type_id: int

    @field_validator("phone_number", mode='before')
    def validate_phone_number(cls, v):
        # Strip any whitespace
        v = v.strip()
        # Validate Uzbekistan phone number format
        if not v.startswith("+998") or len(v) != 13 or not v[4:].isdigit():
            raise ValueError("Phone number must be in format +998XXXXXXXXX")
        return v


class UserCreate(BaseModel):
    """Schema for creating a user"""
    phone_number: str
    username: Optional[str] = None
    password: str = Field(..., min_length=6)
    role: UserRole
    
    @field_validator("phone_number", mode='before')
    def validate_phone_number(cls, v):
        # Strip any whitespace
        v = v.strip()
        # Validate Uzbekistan phone number format
        if not v.startswith("+998") or len(v) != 13 or not v[4:].isdigit():
            raise ValueError("Phone number must be in format +998XXXXXXXXX")
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    phone_number: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    """Response schema for user"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PhoneNumberCheck(BaseModel):
    """Schema for phone number existence check"""
    phone_number: str
    user_type_id: int

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


class StudentInfoBase(BaseModel):
    """Base schema for student info"""
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[Genders] = None
    school: int
    shift: Optional[Shifts] = None
    father: Optional[int] = None
    mother: Optional[int] = None


class StudentInfoCreate(StudentInfoBase):
    """Schema for creating student info"""
    user_id: int


class StudentInfoUpdate(BaseModel):
    """Schema for updating student info"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    patronymic: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[Genders] = None
    school: Optional[int] = None
    shift: Optional[Shifts] = None
    father: Optional[int] = None
    mother: Optional[int] = None


class StudentInfoResponse(StudentInfoBase):
    """Response schema for student info"""
    id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)


class ParentInfoBase(BaseModel):
    """Base schema for parent info"""
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[Genders] = None
    passport_id: Optional[str] = None


class ParentInfoCreate(ParentInfoBase):
    """Schema for creating parent info"""
    user_id: int


class ParentInfoUpdate(BaseModel):
    """Schema for updating parent info"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    patronymic: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[Genders] = None
    passport_id: Optional[str] = None


class ParentInfoResponse(ParentInfoBase):
    """Response schema for parent info"""
    id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    """Schema for login requests"""
    phone_number: str
    password: str
    user_type_id: int

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
    user_type_id: int
    expires_at: int  # Unix timestamp


class UserPreferenceBase(BaseModel):
    """Base schema for user preferences"""
    language: Optional[Languages] = None
    theme: Optional[Themes] = None


class UserPreferenceCreate(UserPreferenceBase):
    """Schema for creating user preferences"""
    user_id: int


class UserPreferenceUpdate(UserPreferenceBase):
    """Schema for updating user preferences"""
    pass


class UserPreferenceResponse(UserPreferenceBase):
    """Response schema for user preferences"""
    id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)
