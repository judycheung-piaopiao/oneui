"""
Simple migration script - sync version
"""
import psycopg2
from psycopg2.extras import Json

# Database connection
conn = psycopg2.connect(
    host="10.40.1.56",
    port=5432,
    database="one_ag",
    user="one_rw",
    password="ONEAG@2025"
)

cur = conn.cursor()

# Fetch data from cataloguedata
cur.execute("SELECT tools, link, documentation, keywords, description FROM cataloguedata")
rows = cur.fetchall()

print(f"Found {len(rows)} records in cataloguedata")

migrated = 0
skipped = 0

for row in rows:
    tool_name, link, documentation, keywords, description = row
    
    if not tool_name or not link:
        print(f"⏭️  Skipping row with missing name or link")
        skipped += 1
        continue
    
    if not description:
        description = f"{tool_name} tool"
    
    # Insert into tools table
    cur.execute("""
        INSERT INTO tools (id, name, description, icon, tool_link, documentation_link, keywords, tags)
        VALUES (gen_random_uuid()::text, %s, %s, %s, %s, %s, %s, %s)
    """, (tool_name, description, "🔧", link, documentation, keywords, Json([])))
    
    migrated += 1
    print(f"✅ Migrated: {tool_name}")

conn.commit()
cur.close()
conn.close()

print(f"\n✅ Migration complete! Migrated: {migrated}, Skipped: {skipped}")
