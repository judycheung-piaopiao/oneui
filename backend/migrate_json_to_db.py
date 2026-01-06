"""
Migration script to import data from JSON file to PostgreSQL database
Run this script to migrate existing tools.json data to the database
"""
import asyncio
import json
import sys
from pathlib import Path
from app.db.base import AsyncSessionLocal
from app.db.models import ToolDB
from app.core.config import settings


async def migrate_json_to_db():
    """
    Import tools from JSON file to database
    """
    json_file = Path(settings.DATA_DIR) / settings.TOOLS_FILE
    
    if not json_file.exists():
        print(f"❌ JSON file not found: {json_file}")
        print("No data to migrate.")
        return
    
    print(f"📂 Reading data from {json_file}...")
    with open(json_file, 'r') as f:
        tools_data = json.load(f)
    
    print(f"Found {len(tools_data)} tools to migrate")
    
    async with AsyncSessionLocal() as session:
        migrated_count = 0
        skipped_count = 0
        
        for tool_dict in tools_data:
            try:
                # Check if tool already exists
                existing = await session.get(ToolDB, tool_dict["id"])
                if existing:
                    print(f"⏭️  Skipping '{tool_dict['name']}' (already exists)")
                    skipped_count += 1
                    continue
                
                # Create new tool
                tool_db = ToolDB(**tool_dict)
                session.add(tool_db)
                migrated_count += 1
                print(f"✅ Migrated: {tool_dict['name']}")
                
            except Exception as e:
                print(f"❌ Error migrating '{tool_dict.get('name', 'Unknown')}': {e}")
        
        # Commit all changes
        await session.commit()
        
        print("\n" + "=" * 50)
        print(f"✅ Migration complete!")
        print(f"   Migrated: {migrated_count}")
        print(f"   Skipped: {skipped_count}")
        print(f"   Total: {len(tools_data)}")
        print("=" * 50)


if __name__ == "__main__":
    try:
        asyncio.run(migrate_json_to_db())
    except KeyboardInterrupt:
        print("\n⚠️  Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)
