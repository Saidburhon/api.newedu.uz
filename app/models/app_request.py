from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM

from app.core.database import Base
from app.models.enums import AppRequestStatuses


class AppRequest(Base):
    """App Request model"""
    __tablename__ = "app_request"
    
    id = Column(Integer, primary_key=True)
    app_id = Column(Integer, ForeignKey("app.id"), nullable=False)
    from_user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    reason = Column(Text)
    status = Column(ENUM(AppRequestStatuses), name="app_request_statuses", default="pending")
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    app = relationship("App", back_populates="app_requests")
    from_user = relationship("User", foreign_keys=[from_user_id], back_populates="app_requests")
    logs = relationship("AppRequestLog", back_populates="app_request")


class AppRequestLog(Base):
    """App Request Log model"""
    __tablename__ = "app_requests_log"
    
    id = Column(Integer, primary_key=True)
    app_request_id = Column(Integer, ForeignKey("app_request.id"), nullable=False)
    status_was = Column(ENUM(AppRequestStatuses), name="app_request_statuses")
    status_changed_to = Column(ENUM(AppRequestStatuses), name="app_request_statuses")
    responsible_admin_id = Column(Integer, ForeignKey("user.id"))
    basis = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    
    # Relationships
    app_request = relationship("AppRequest", back_populates="logs")
    responsible_admin = relationship("User", back_populates="app_request_logs")
