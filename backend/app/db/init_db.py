"""
Database initialization script
"""
import asyncio
from app.db.base import engine, Base
from app.db.models import ToolDB


async def init_db():
    """
    Create all tables in the database
    """
    print("Creating database tables...")
    async with engine.begin() as conn:
        # Drop all tables (comment this out in production)
        # await conn.run_sync(Base.metadata.drop_all)
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created successfully!")


async def drop_all_tables():
    """
    Drop all tables (use with caution!)
    """
    print("⚠️  Dropping all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("✅ All tables dropped!")


if __name__ == "__main__":
    # Run initialization
    asyncio.run(init_db())
