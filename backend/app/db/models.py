"""
Database models
"""
from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.db.base import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class ToolDB(Base):
    __tablename__ = "tools"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    icon = Column(String(500), nullable=False, default="🔧")  # Increased to 500 for URLs
    tool_link = Column(String(500), nullable=False)
    documentation_link = Column(String(500), nullable=True)
    keywords = Column(Text, nullable=True)  # For AI search (comma-separated text)
    tags = Column(JSON, nullable=False, default=list)  # For filtering (HR, Trader, DevOps, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "tool_link": self.tool_link,
            "documentation_link": self.documentation_link if self.documentation_link else None,
            "keywords": self.keywords,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
