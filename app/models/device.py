from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM

from app.core.database import Base
from app.models.enums import OsTypes, AndroidUI, PhoneBrands, ActionDegrees


class OS(Base):
    """Operating System model"""
    __tablename__ = "os"
    
    id = Column(Integer, primary_key=True)
    type = Column(ENUM(OsTypes), name="os_types", nullable=False)
    version = Column(String)
    ui = Column(ENUM(AndroidUI), name="android_ui")
    ui_version = Column(String)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    
    # Relationships
    devices = relationship("Device", back_populates="os")


class Device(Base):
    """Device model"""
    __tablename__ = "device"
    
    id = Column(Integer, primary_key=True)
    brand = Column(ENUM(PhoneBrands), name="phone_brands")
    model = Column(String)
    os_id = Column(Integer, ForeignKey("os.id"))
    ram = Column(Integer)
    storage = Column(Integer)
    IMEI = Column(String)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    
    # Relationships
    os = relationship("OS", back_populates="devices")
    user_devices = relationship("UserDevice", back_populates="device")


class UserDevice(Base):
    """User Device model"""
    __tablename__ = "user_devices"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("device.id"), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="user_devices")
    device = relationship("Device", back_populates="user_devices")
    logs = relationship("Log", back_populates="user_device")
    setups = relationship("Setup", back_populates="user_device")
    user_apps = relationship("UserApp", back_populates="user_device")
    
    # Unique constraint
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )


class Action(Base):
    """Action model"""
    __tablename__ = "action"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    degree = Column(ENUM(ActionDegrees), name="action_degrees")
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    
    # Relationships
    logs = relationship("Log", back_populates="action")


class Log(Base):
    """Log model"""
    __tablename__ = "log"
    
    id = Column(Integer, primary_key=True)
    user_devices_id = Column(Integer, ForeignKey("user_devices.id"), nullable=False)
    user_app_id = Column(Integer, ForeignKey("user_apps.id"))
    action_id = Column(Integer, ForeignKey("action.id"), nullable=False)
    done_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    location = Column(String)
    details = Column(String)
    
    # Relationships
    user_device = relationship("UserDevice", back_populates="logs")
    user_app = relationship("UserApp", back_populates="logs")
    action = relationship("Action", back_populates="logs")


class Setup(Base):
    """Setup model"""
    __tablename__ = "setup"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user_device_id = Column(Integer, ForeignKey("user_devices.id"), nullable=False)
    camera = Column(Boolean)
    location = Column(Boolean)
    usage_access = Column(Boolean)
    admin_app = Column(Boolean)
    accessibility_features = Column(Boolean)
    pop_up = Column(Boolean)
    notification_service = Column(Boolean)
    battery_optimization = Column(Boolean)
    gps = Column(Boolean)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="setups")
    user_device = relationship("UserDevice", back_populates="setups")


class UserApp(Base):
    """User App model"""
    __tablename__ = "user_apps"
    
    id = Column(Integer, primary_key=True)
    user_devices_id = Column(Integer, ForeignKey("user_devices.id"), nullable=False)
    app_id = Column(Integer, ForeignKey("app.id"), nullable=False)
    added_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user_device = relationship("UserDevice", back_populates="user_apps")
    app = relationship("App", back_populates="user_apps")
    logs = relationship("Log", back_populates="user_app")
    
    # Unique constraint
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )
