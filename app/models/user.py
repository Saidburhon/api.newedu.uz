from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Boolean, Text, Numeric, JSON, func, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM

from app.core.database import Base
from app.models.enums import (
    Priorities, Genders, Shifts, OsTypes, AndroidUI, PhoneBrands, 
    ActionDegrees, Languages, Themes, AppType, AppRequestStatuses, GeneralType
)


class UserTask(Base):
    """User tasks model"""
    __tablename__ = "user_tasks"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey("user.id"))
    type = Column(String)
    priority = Column(ENUM(Priorities), name="priorities")
    scheduled_to = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="tasks")


class UserType(Base):
    """User type model"""
    __tablename__ = "user_type"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    user_level = Column(Integer)
    school = Column(Integer, ForeignKey("schools.id"))
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="user_type_rel")
    school_rel = relationship("School", back_populates="user_types")
    policies = relationship("Policy", back_populates="targeted_user_type")


class Website(Base):
    """Website model"""
    __tablename__ = "website"
    
    id = Column(Integer, primary_key=True)
    domain = Column(String, nullable=False, unique=True)
    icon = Column(String)
    visit_count = Column(Integer, default=0)
    type = Column(String)
    added_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    
    # Relationships
    policy_webs = relationship("PolicyWeb", back_populates="website")


class App(Base):
    """App model"""
    __tablename__ = "app"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    package = Column(String, unique=True)
    icon = Column(String)
    install_count = Column(Integer, default=0)
    type = Column(ENUM(AppType), name="app_type")
    added_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    
    # Relationships
    policy_apps = relationship("PolicyApp", back_populates="app")
    app_requests = relationship("AppRequest", back_populates="app")
    user_apps = relationship("UserApp", back_populates="app")


class Policy(Base):
    """Policy model"""
    __tablename__ = "policy"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    is_whitelist_app = Column(Boolean, default=True)
    is_whitelist_web = Column(Boolean, default=True)
    targeted_user_type_id = Column(Integer, ForeignKey("user_type.id"))
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    targeted_user_type = relationship("UserType", back_populates="policies")
    policy_apps = relationship("PolicyApp", back_populates="policy")
    policy_webs = relationship("PolicyWeb", back_populates="policy")
    schools = relationship("School", back_populates="policy")


class PolicyApp(Base):
    """Policy App model"""
    __tablename__ = "policy_app"
    
    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey("policy.id"), nullable=False)
    app_id = Column(Integer, ForeignKey("app.id"), nullable=False)
    duration = Column(Integer)
    
    # Relationships
    policy = relationship("Policy", back_populates="policy_apps")
    app = relationship("App", back_populates="policy_apps")
    
    # Indexes
    __table_args__ = (Index('app_duration_unique', 'app_id', 'duration', unique=True),)


class PolicyWeb(Base):
    """Policy Web model"""
    __tablename__ = "policy_web"
    
    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey("policy.id"), nullable=False)
    website_id = Column(Integer, ForeignKey("website.id"), nullable=False)
    duration = Column(Integer)
    
    # Relationships
    policy = relationship("Policy", back_populates="policy_webs")
    website = relationship("Website", back_populates="policy_webs")
    
    # Indexes
    __table_args__ = (Index('website_duration_unique', 'website_id', 'duration', unique=True),)


class Region(Base):
    """Region model"""
    __tablename__ = "regions"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    
    # Relationships
    cities = relationship("City", back_populates="region")
    districts = relationship("District", back_populates="region")
    schools = relationship("School", back_populates="region_rel")


class City(Base):
    """City model"""
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    parent_region = Column(Integer, ForeignKey("regions.id"))
    
    # Relationships
    region = relationship("Region", back_populates="cities")
    schools = relationship("School", back_populates="city_rel")


class District(Base):
    """District model"""
    __tablename__ = "districts"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    parent_region = Column(Integer, ForeignKey("regions.id"))
    
    # Relationships
    region = relationship("Region", back_populates="districts")
    schools = relationship("School", back_populates="district_rel")


class School(Base):
    """School model"""
    __tablename__ = "schools"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    region = Column(Integer, ForeignKey("regions.id"))
    city = Column(Integer, ForeignKey("cities.id"))
    district = Column(Integer, ForeignKey("districts.id"))
    address = Column(String)
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    location = Column(JSON)
    radius = Column(Numeric)
    policy_id = Column(Integer, ForeignKey("policy.id"))
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    region_rel = relationship("Region", back_populates="schools")
    city_rel = relationship("City", back_populates="schools")
    district_rel = relationship("District", back_populates="schools")
    policy = relationship("Policy", back_populates="schools")
    user_types = relationship("UserType", back_populates="school_rel")
    student_infos = relationship("StudentInfo", back_populates="school_rel")


class User(Base):
    """User model"""
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    phone_number = Column(String)
    user_type_id = Column(Integer, ForeignKey("user_type.id"))
    password_hash = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user_type_rel = relationship("UserType", back_populates="users")
    student_info = relationship("StudentInfo", foreign_keys="StudentInfo.user_id", back_populates="user")
    father_of = relationship("StudentInfo", foreign_keys="StudentInfo.father", back_populates="father_rel")
    mother_of = relationship("StudentInfo", foreign_keys="StudentInfo.mother", back_populates="mother_rel")
    parent_info = relationship("ParentInfo", back_populates="user")
    app_requests = relationship("AppRequest", foreign_keys="AppRequest.from_user_id", back_populates="from_user")
    app_request_logs = relationship("AppRequestLog", back_populates="responsible_admin")
    tasks = relationship("UserTask", back_populates="user")
    user_devices = relationship("UserDevice", back_populates="user")
    setups = relationship("Setup", back_populates="user")
    preferences = relationship("UserPreference", back_populates="user")
    
    # Indexes
    __table_args__ = (Index('user_phone_type_unique', 'phone_number', 'user_type_id', unique=True),)


class StudentInfo(Base):
    """Student Info model"""
    __tablename__ = "student_info"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    patronymic = Column(String)
    age = Column(Integer)
    gender = Column(ENUM(Genders), name="genders")
    school = Column(Integer, ForeignKey("schools.id"), nullable=False)
    shift = Column(ENUM(Shifts), name="shifts")
    father = Column(Integer, ForeignKey("user.id"))
    mother = Column(Integer, ForeignKey("user.id"))
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="student_info")
    school_rel = relationship("School", back_populates="student_infos")
    father_rel = relationship("User", foreign_keys=[father], back_populates="father_of")
    mother_rel = relationship("User", foreign_keys=[mother], back_populates="mother_of")


class ParentInfo(Base):
    """Parent Info model"""
    __tablename__ = "parent_info"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    patronymic = Column(String)
    age = Column(Integer)
    gender = Column(ENUM(Genders), name="genders")
    passport_id = Column(String)
    
    # Relationships
    user = relationship("User", back_populates="parent_info")
