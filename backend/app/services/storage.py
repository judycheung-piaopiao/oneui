"""
PostgreSQL database storage service
"""
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tool import Tool, ToolCreate, ToolUpdate
from app.db.base import AsyncSessionLocal
from app.db.models import ToolDB


class StorageService:
    """Database storage service using PostgreSQL"""
    
    async def get_all_tools(self) -> List[Tool]:
        """Get all tools"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(ToolDB))
            tools_db = result.scalars().all()
            return [Tool(**tool.to_dict()) for tool in tools_db]
    
    async def get_tool_by_id(self, tool_id: str) -> Optional[Tool]:
        """Get tool by ID"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ToolDB).where(ToolDB.id == tool_id)
            )
            tool_db = result.scalar_one_or_none()
            return Tool(**tool_db.to_dict()) if tool_db else None
    
    async def create_tool(self, tool_data: ToolCreate) -> Tool:
        """Create new tool"""
        async with AsyncSessionLocal() as session:
            # Convert Pydantic model to dict and handle HttpUrl
            tool_dict = tool_data.model_dump()
            tool_dict["tool_link"] = str(tool_dict["tool_link"])
            if tool_dict.get("documentation_link"):
                tool_dict["documentation_link"] = str(tool_dict["documentation_link"])
            
            # Create database model
            tool_db = ToolDB(**tool_dict)
            session.add(tool_db)
            await session.commit()
            await session.refresh(tool_db)
            
            return Tool(**tool_db.to_dict())
    
    async def update_tool(self, tool_id: str, tool_data: ToolUpdate) -> Optional[Tool]:
        """Update existing tool"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ToolDB).where(ToolDB.id == tool_id)
            )
            tool_db = result.scalar_one_or_none()
            
            if not tool_db:
                return None
            
            # Update only provided fields
            update_data = tool_data.model_dump(exclude_unset=True)
            
            # Handle HttpUrl conversion
            if "tool_link" in update_data and update_data["tool_link"]:
                update_data["tool_link"] = str(update_data["tool_link"])
            if "documentation_link" in update_data and update_data["documentation_link"]:
                update_data["documentation_link"] = str(update_data["documentation_link"])
            
            for key, value in update_data.items():
                setattr(tool_db, key, value)
            
            await session.commit()
            await session.refresh(tool_db)
            
            return Tool(**tool_db.to_dict())
    
    async def delete_tool(self, tool_id: str) -> bool:
        """Delete tool"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ToolDB).where(ToolDB.id == tool_id)
            )
            tool_db = result.scalar_one_or_none()
            
            if not tool_db:
                return False
            
            await session.delete(tool_db)
            await session.commit()
            return True


storage = StorageService()
