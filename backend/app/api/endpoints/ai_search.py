"""
AI Search endpoint - independent from regular search
"""
from fastapi import APIRouter, Query
from typing import List
from pydantic import BaseModel

from app.services.storage import storage
from app.services.ai_search import ai_search_service

router = APIRouter()


class AISearchResult(BaseModel):
    """AI search result with relevance score"""
    id: str
    name: str
    description: str
    icon: str | None
    tool_link: str
    documentation_link: str | None
    tags: List[str]
    score: float  # Relevance score 0-1


class AISearchResponse(BaseModel):
    """AI search response"""
    query: str
    results: List[AISearchResult]
    total: int


@router.get("/ai-search", response_model=AISearchResponse)
async def ai_search(
    q: str = Query(..., description="Search query in natural language"),
    limit: int = Query(10, ge=1, le=50, description="Max number of results")
):
    """
    AI-powered semantic search
    
    Examples:
    - "trading tools" - finds trading-related tools
    - "监控系统" - finds monitoring tools (Chinese)
    - "HR management" - finds HR tools
    - "devops dashboard" - finds DevOps tools
    """
    # Get all tools
    all_tools = await storage.get_all_tools()
    
    # Perform AI search
    search_results = ai_search_service.search(
        query=q,
        tools=all_tools,
        top_k=limit,
        min_score=0.1  # Filter out very low relevance results
    )
    
    # Convert to response format
    results = [
        AISearchResult(
            id=tool.id,
            name=tool.name,
            description=tool.description,
            icon=tool.icon,
            tool_link=str(tool.tool_link),
            documentation_link=str(tool.documentation_link) if tool.documentation_link else None,
            tags=tool.tags,
            score=round(score, 3)
        )
        for tool, score in search_results
    ]
    
    return AISearchResponse(
        query=q,
        results=results,
        total=len(results)
    )
