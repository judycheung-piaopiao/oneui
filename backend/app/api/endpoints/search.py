"""
Search endpoints with AI/NLP integration
"""
from fastapi import APIRouter, Query
from typing import List, Optional
from app.models.tool import Tool
from app.services.storage import storage

router = APIRouter()


@router.get("", response_model=List[Tool])
async def search_tools(
    q: Optional[str] = Query(None, description="Search query"),
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter by")
):
    """
    Search tools with intelligent filtering
    - Search by name, description
    - Filter by tags
    - Future: NLP/AI semantic search
    """
    all_tools = await storage.get_all_tools()
    
    # Filter by tags
    if tags:
        tag_list = [t.strip().lower() for t in tags.split(",")]
        all_tools = [
            tool for tool in all_tools
            if any(tag.lower() in [t.lower() for t in tool.tags] for tag in tag_list)
        ]
    
    # Search by query
    if q:
        query_lower = q.lower()
        all_tools = [
            tool for tool in all_tools
            if (query_lower in tool.name.lower() or
                query_lower in tool.description.lower() or
                any(query_lower in tag.lower() for tag in tool.tags))
        ]
    
    return all_tools


@router.get("/suggest")
async def suggest_tools(q: str = Query(..., description="Query for suggestions")):
    """
    Get tool suggestions based on query
    Future: AI-powered recommendations
    """
    all_tools = await storage.get_all_tools()
    query_lower = q.lower()
    
    # Simple keyword matching for now
    suggestions = [
        {
            "id": tool.id,
            "name": tool.name,
            "tags": tool.tags
        }
        for tool in all_tools
        if query_lower in tool.name.lower() or query_lower in tool.description.lower()
    ]
    
    return {"suggestions": suggestions[:5]}  # Limit to 5 suggestions
