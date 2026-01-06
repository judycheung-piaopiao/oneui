"""
Tools CRUD endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from typing import List
from app.models.tool import Tool, ToolCreate, ToolUpdate
from app.services.storage import storage
from app.core.auth import User, get_current_user, require_admin
from app.services.document_rag import rag_service
from app.services.document_crawler import DocumentCrawler

router = APIRouter()


@router.get("", response_model=List[Tool])
async def get_all_tools():
    """Get all tools"""
    return await storage.get_all_tools()


@router.get("/{tool_id}", response_model=Tool)
async def get_tool(tool_id: str):
    """Get tool by ID"""
    tool = await storage.get_tool_by_id(tool_id)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool with id {tool_id} not found"
        )
    return tool


@router.post("", response_model=Tool, status_code=status.HTTP_201_CREATED)
async def create_tool(
    tool: ToolCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Create new tool (Admin only) - automatically indexes documentation"""
    require_admin(current_user)
    new_tool = await storage.create_tool(tool)
    
    # Auto-index documentation in background
    if new_tool.documentation_link:
        async def index_docs():
            try:
                crawler = DocumentCrawler()
                content = await crawler.fetch_url(new_tool.documentation_link)
                if content:
                    rag_service.index_document(
                        tool_id=new_tool.id,
                        tool_name=new_tool.name,
                        doc_url=new_tool.documentation_link,
                        content=content,
                        doc_type="webpage"
                    )
                    print(f"✅ Auto-indexed docs for new tool: {new_tool.name}")
            except Exception as e:
                print(f"⚠️ Failed to auto-index docs for {new_tool.name}: {e}")
        
        background_tasks.add_task(index_docs)
    
    return new_tool


@router.put("/{tool_id}", response_model=Tool)
async def update_tool(
    tool_id: str, 
    tool: ToolUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Update existing tool (Admin only) - re-indexes documentation if link changed"""
    require_admin(current_user)
    updated_tool = await storage.update_tool(tool_id, tool)
    if not updated_tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool with id {tool_id} not found"
        )
    
    # Re-index documentation if link was updated
    if tool.documentation_link:
        async def reindex_docs():
            try:
                # Delete old docs first
                rag_service.delete_tool_documents(tool_id)
                
                # Index new docs
                crawler = DocumentCrawler()
                content = await crawler.fetch_url(tool.documentation_link)
                if content:
                    rag_service.index_document(
                        tool_id=updated_tool.id,
                        tool_name=updated_tool.name,
                        doc_url=tool.documentation_link,
                        content=content,
                        doc_type="webpage"
                    )
                    print(f"✅ Re-indexed docs for updated tool: {updated_tool.name}")
            except Exception as e:
                print(f"⚠️ Failed to re-index docs for {updated_tool.name}: {e}")
        
        background_tasks.add_task(reindex_docs)
    
    return updated_tool


@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(
    tool_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete tool (Admin only)"""
    require_admin(current_user)
    success = await storage.delete_tool(tool_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool with id {tool_id} not found"
        )
