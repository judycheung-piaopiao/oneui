"""
Tool data models
"""
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime


class ToolBase(BaseModel):
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    icon: Optional[str] = Field(None, description="Icon URL or emoji")
    tool_link: HttpUrl = Field(..., description="Link to the tool")
    documentation_link: Optional[HttpUrl] = Field(None, description="Link to documentation")
    keywords: Optional[str] = Field(None, description="Keywords for AI search (comma-separated)")
    tags: List[str] = Field(default_factory=list, description="Category tags (HR, Trader, DevOps, etc.)")


class ToolCreate(ToolBase):
    pass


class ToolUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    tool_link: Optional[HttpUrl] = None
    documentation_link: Optional[HttpUrl] = None
    keywords: Optional[str] = None
    tags: Optional[List[str]] = None


class Tool(ToolBase):
    id: str = Field(..., description="Unique tool ID")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "tool-001",
                "name": "DevOps Dashboard",
                "description": "Central hub for all DevOps tools and monitoring",
                "icon": "🛠️",
                "tool_link": "http://devops.alpha-grep.com:5000",
                "documentation_link": "http://devops.alpha-grep.com:5000/docs",
                "tags": ["devops", "monitoring", "admin"],
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }
