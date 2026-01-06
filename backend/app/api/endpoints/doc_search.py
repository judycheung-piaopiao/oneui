"""
Document Search API Endpoints
Provides semantic search over tool documentation
"""
from fastapi import APIRouter, BackgroundTasks, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.services.document_rag import rag_service
from app.services.document_crawler import crawler
from app.services.storage import storage

router = APIRouter()


class DocumentSearchResult(BaseModel):
    """Single document search result"""
    tool_id: str
    tool_name: str
    content_snippet: str
    doc_url: str
    doc_type: str
    relevance_score: float


class DocumentSearchResponse(BaseModel):
    """Response for document search"""
    query: str
    results: List[DocumentSearchResult]
    total: int


class IndexResponse(BaseModel):
    """Response for indexing operations"""
    message: str
    tool_id: Optional[str] = None
    chunks_indexed: Optional[int] = None


class StatsResponse(BaseModel):
    """Document index statistics"""
    total_chunks: int
    total_tools: int
    model_dimension: int


@router.get("/doc-search", response_model=DocumentSearchResponse)
async def search_documents(
    q: str = Query(..., description="Search query in natural language", min_length=2),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    min_score: float = Query(0.3, ge=0.0, le=1.0, description="Minimum relevance score")
):
    """
    🔍 Semantic search over tool documentation
    
    This endpoint searches through indexed documentation using AI embeddings,
    allowing natural language queries in English or Chinese.
    
    **Examples:**
    - "如何部署 strategy GUI" (Chinese)
    - "troubleshooting RKV connection"
    - "eye service configuration"
    - "authentication setup"
    
    **Returns:**
    - Relevant document snippets
    - Source tool and documentation URL
    - Relevance scores (0-1)
    """
    try:
        # Perform semantic search
        results = rag_service.search(
            query=q,
            top_k=limit,
            min_score=min_score
        )
        
        # Format results
        formatted_results = []
        for result in results:
            # Use smart summary if available, otherwise truncate content
            snippet = result.get('summary', result['content'])
            if len(snippet) > 300:
                snippet = snippet[:297] + "..."
            
            formatted_results.append(
                DocumentSearchResult(
                    tool_id=result['tool_id'],
                    tool_name=result['tool_name'],
                    content_snippet=snippet,
                    doc_url=result['doc_url'],
                    doc_type=result['doc_type'],
                    relevance_score=result['relevance_score']
                )
            )
        
        return DocumentSearchResponse(
            query=q,
            results=formatted_results,
            total=len(formatted_results)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.post("/index-tool-docs/{tool_id}", response_model=IndexResponse)
async def index_tool_documentation(
    tool_id: str,
    background_tasks: BackgroundTasks
):
    """
    📚 Index documentation for a specific tool
    
    This endpoint crawls the tool's documentation URL and indexes it
    for semantic search. The indexing happens in the background.
    
    **What it does:**
    1. Fetches the documentation from the tool's doc URL
    2. Splits it into searchable chunks
    3. Generates AI embeddings
    4. Stores in vector database
    
    **Note:** Indexing happens asynchronously. The tool's documentation
    will be searchable within a few seconds.
    """
    # Get tool from storage
    tool = await storage.get_tool(tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool {tool_id} not found")
    
    if not tool.documentation_link:
        raise HTTPException(
            status_code=400, 
            detail=f"Tool {tool.name} has no documentation link"
        )
    
    async def index_task():
        """Background task to index documentation"""
        try:
            print(f"Starting indexing for {tool.name}...")
            
            # Fetch documentation content
            content = crawler.fetch_url(str(tool.documentation_link))
            
            if not content:
                print(f"Warning: Could not fetch content from {tool.documentation_link}")
                return
            
            # Index the document
            chunks_count = rag_service.index_document(
                tool_id=tool.id,
                tool_name=tool.name,
                doc_url=str(tool.documentation_link),
                content=content,
                doc_type="confluence" if "confluence" in str(tool.documentation_link).lower() else "webpage"
            )
            
            print(f"Successfully indexed {chunks_count} chunks for {tool.name}")
            
        except Exception as e:
            print(f"Error indexing {tool.name}: {e}")
    
    # Add to background tasks
    background_tasks.add_task(index_task)
    
    return IndexResponse(
        message=f"Started indexing documentation for {tool.name}",
        tool_id=tool.id
    )


@router.post("/reindex-all-docs", response_model=IndexResponse)
async def reindex_all_documents(background_tasks: BackgroundTasks):
    """
    🔄 Reindex all tool documentation
    
    This endpoint reindexes documentation for ALL tools that have
    documentation links. Use this to refresh the search index.
    
    **Warning:** This can take several minutes depending on the
    number of tools. The operation runs in the background.
    
    **Use cases:**
    - Documentation has been updated
    - Initial setup of the search system
    - Fixing indexing errors
    """
    async def reindex_task():
        """Background task to reindex all documentation"""
        try:
            print("Starting full reindex of all documentation...")
            
            # Get all tools
            all_tools = await storage.get_all_tools()
            
            indexed_count = 0
            failed_count = 0
            
            for tool in all_tools:
                if not tool.documentation_link:
                    continue
                
                try:
                    # Fetch content
                    content = crawler.fetch_url(str(tool.documentation_link))
                    
                    if content:
                        # Index document
                        chunks = rag_service.index_document(
                            tool_id=tool.id,
                            tool_name=tool.name,
                            doc_url=str(tool.documentation_link),
                            content=content,
                            doc_type="confluence" if "confluence" in str(tool.documentation_link).lower() else "webpage"
                        )
                        
                        if chunks > 0:
                            indexed_count += 1
                    else:
                        failed_count += 1
                        print(f"Failed to fetch content for {tool.name}")
                
                except Exception as e:
                    failed_count += 1
                    print(f"Error indexing {tool.name}: {e}")
            
            print(f"Reindex complete: {indexed_count} tools indexed, {failed_count} failed")
            
        except Exception as e:
            print(f"Error during reindex: {e}")
    
    # Add to background tasks
    background_tasks.add_task(reindex_task)
    
    return IndexResponse(
        message="Started reindexing all tool documentation. This may take several minutes."
    )


@router.delete("/index-tool-docs/{tool_id}", response_model=IndexResponse)
async def delete_tool_documentation(tool_id: str):
    """
    🗑️ Delete indexed documentation for a tool
    
    Removes all document chunks for a specific tool from the search index.
    
    **Use cases:**
    - Tool is being deleted
    - Documentation URL changed (delete then reindex)
    - Cleaning up old data
    """
    tool = await storage.get_tool(tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool {tool_id} not found")
    
    success = rag_service.delete_tool_documents(tool_id)
    
    if success:
        return IndexResponse(
            message=f"Deleted documentation index for {tool.name}",
            tool_id=tool.id
        )
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete documentation for {tool.name}"
        )


@router.get("/doc-stats", response_model=StatsResponse)
async def get_documentation_stats():
    """
    📊 Get statistics about the document index
    
    Returns information about how many documents and tools are indexed.
    
    **Useful for:**
    - Monitoring the search system
    - Checking if indexing is complete
    - Debugging
    """
    stats = rag_service.get_stats()
    
    return StatsResponse(
        total_chunks=stats.get("total_chunks", 0),
        total_tools=stats.get("total_tools", 0),
        model_dimension=stats.get("model", 384)
    )
