from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Enum, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """Base user model that contains common fields for all user types"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    user_type = Column(Enum('student', 'teacher', 'admin'), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(),
                      onupdate=func.current_timestamp())
    
    # Relationships defined in subclass models
    

class Student(Base):
    """Student model with education related fields"""
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    school = Column(String(255), nullable=False)
    grade = Column(Integer, nullable=False)  # 1-11
    class_id = Column(String(50), nullable=False)  # Class letter ID (A, B, C, etc.)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(),
                      onupdate=func.current_timestamp())


class Teacher(Base):
    """Teacher model with teaching related fields"""
    __tablename__ = "teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    school = Column(String(255), nullable=False)
    subjects = Column(Text, nullable=True)  # CSV of subjects or could be a relation table
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(),
                      onupdate=func.current_timestamp())


class Admin(Base):
    """Admin model with admin-specific fields"""
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    role = Column(String(100), nullable=False, default="staff")  # roles like staff, super_admin, etc.
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(),
                      onupdate=func.current_timestamp())
