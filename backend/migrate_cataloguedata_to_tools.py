"""
Migration script to import data from cataloguedata table to tools table
Maps the old schema to the new schema
"""
import asyncio
import sys
from sqlalchemy import text
from app.db.base import AsyncSessionLocal, engine
from app.db.models import ToolDB


async def migrate_cataloguedata_to_tools():
    """
    Migrate data from cataloguedata table to tools table
    
    Field mapping:
    - cataloguedata.tools -> tools.name
    - cataloguedata.link -> tools.tool_link
    - cataloguedata.documentation -> tools.documentation_link
    - cataloguedata.keywords -> tools.keywords (keep as text for AI search)
    - cataloguedata.description -> tools.description
    - tags: empty array [] (to be filled manually with HR, Trader, DevOps, etc.)
    - icon: default to 🔧
    """
    print("=" * 60)
    print("Migrating data from cataloguedata to tools table")
    print("=" * 60)
    
    async with AsyncSessionLocal() as session:
        # Check if cataloguedata table exists and has data
        result = await session.execute(
            text("SELECT tools, link, documentation, keywords, description FROM cataloguedata")
        )
        rows = result.fetchall()
        
        if not rows:
            print("❌ No data found in cataloguedata table")
            return
        
        print(f"📊 Found {len(rows)} records in cataloguedata")
        print()
        
        migrated_count = 0
        error_count = 0
        
        for row in rows:
            try:
                tool_name = row[0]  # tools
                tool_link = row[1]  # link
                documentation = row[2]  # documentation
                keywords = row[3]  # keywords
                description = row[4]  # description
                
                # Skip if name or link is empty
                if not tool_name or not tool_link:
                    print(f"⏭️  Skipping row with missing name or link")
                    continue
                
                # Use description or generate one
                if not description or description.strip() == '':
                    description = f"{tool_name} tool"
                
                # Create new tool entry
                tool_db = ToolDB(
                    name=tool_name,
                    description=description,
                    icon="🔧",  # Default icon
                    tool_link=tool_link if tool_link else "http://localhost",
                    documentation_link=documentation if documentation else None,
                    keywords=keywords,  # Keep original keywords for AI search
                    tags=[]  # Empty, to be filled manually with HR, Trader, DevOps, etc.
                )
                
                session.add(tool_db)
                migrated_count += 1
                print(f"✅ Migrated: {tool_name}")
                
            except Exception as e:
                error_count += 1
                print(f"❌ Error migrating row: {e}")
                continue
        
        # Commit all changes
        await session.commit()
        
        print()
        print("=" * 60)
        print(f"✅ Migration complete!")
        print(f"   Migrated: {migrated_count}")
        print(f"   Errors: {error_count}")
        print(f"   Total processed: {len(rows)}")
        print("=" * 60)


async def check_migration_result():
    """Check the migration result"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM tools"))
        count = result.scalar()
        print(f"\n📊 Total tools in database: {count}")
        
        # Show sample data
        result = await session.execute(
            text("SELECT name, tool_link, keywords FROM tools LIMIT 5")
        )
        rows = result.fetchall()
        print("\n📝 Sample data:")
        for row in rows:
            keywords_preview = (row[2][:50] + "...") if row[2] and len(row[2]) > 50 else (row[2] or "None")
            print(f"   - {row[0]}: {row[1]}")
            print(f"     Keywords: {keywords_preview}")


if __name__ == "__main__":
    try:
        print("\n🚀 Starting migration...\n")
        asyncio.run(migrate_cataloguedata_to_tools())
        asyncio.run(check_migration_result())
    except KeyboardInterrupt:
        print("\n⚠️  Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
