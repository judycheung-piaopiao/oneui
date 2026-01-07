"""
AG Tools Catalogue - Backend API
FastAPI application for managing internal tools catalogue
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import tools, search, tags, users, ai_search, doc_search, admins
from app.core.config import settings

app = FastAPI(
    title="ONE UI API",
    description="API for managing internal company tools and GUIs",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tools.router, prefix="/api/tools", tags=["tools"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(tags.router, prefix="/api/tags", tags=["tags"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(ai_search.router, prefix="/api", tags=["ai-search"])
app.include_router(doc_search.router, prefix="/api", tags=["doc-search"])
app.include_router(admins.router, prefix="/api/admins", tags=["admins"])


@app.get("/")
async def root():
    return {
        "message": "ONE UI API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
