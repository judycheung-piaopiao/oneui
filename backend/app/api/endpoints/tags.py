"""
Tags endpoints
"""
from fastapi import APIRouter
from typing import List, Dict
from app.services.storage import storage

router = APIRouter()


@router.get("", response_model=List[str])
async def get_all_tags():
    """Get all unique tags across all tools"""
    all_tools = await storage.get_all_tools()
    tags = set()
    for tool in all_tools:
        tags.update(tool.tags)
    return sorted(list(tags))


@router.get("/stats")
async def get_tag_stats():
    """Get statistics for each tag (count of tools)"""
    all_tools = await storage.get_all_tools()
    tag_counts: Dict[str, int] = {}
    
    for tool in all_tools:
        for tag in tool.tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    return {
        "total_tags": len(tag_counts),
        "tags": [
            {"name": tag, "count": count}
            for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        ]
    }
