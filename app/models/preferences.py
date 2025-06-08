from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ENUM

from app.core.database import Base
from app.models.enums import Languages, Themes


class UserPreference(Base):
    """User Preferences model"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    language = Column(ENUM(Languages), name="languages")
    theme = Column(ENUM(Themes), name="themes")
    
    # Relationships
    user = relationship("User", back_populates="preferences")
