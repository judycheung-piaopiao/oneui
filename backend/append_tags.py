"""
Append tags to tools (not replace)
"""
import psycopg2
from psycopg2.extras import Json
import json

conn = psycopg2.connect(
    host="10.40.1.56",
    port=5432,
    database="one_ag",
    user="one_rw",
    password="ONEAG@2025"
)

cur = conn.cursor()

# BD tools (append BD tag)
bd_tools = [
    'AG Trades DB',
    'Holidays',
    'Trading Hours',
    'Corporate Action as Service'
]

# DevOps tools (append DevOps tag)
devops_tools = [
    'RMS UI',
    'AG-config Management System',
    'Holidays',
    'Alerta'
]

def append_tag(tool_name, new_tag):
    """Append a tag to a tool without removing existing tags"""
    # Get current tags
    cur.execute("SELECT tags FROM tools WHERE name = %s", (tool_name,))
    row = cur.fetchone()
    
    if not row:
        print(f"⚠️  Tool not found: {tool_name}")
        return False
    
    current_tags = row[0] if row[0] else []
    
    # Add new tag if not already present
    if new_tag not in current_tags:
        current_tags.append(new_tag)
        cur.execute("UPDATE tools SET tags = %s WHERE name = %s", (Json(current_tags), tool_name))
        print(f"✅ {tool_name}: {current_tags}")
        return True
    else:
        print(f"⏭️  {tool_name} already has '{new_tag}' tag")
        return False

print("Adding BD tags...")
bd_updated = 0
for tool in bd_tools:
    if append_tag(tool, "BD"):
        bd_updated += 1

print(f"\nAdding DevOps tags...")
devops_updated = 0
for tool in devops_tools:
    if append_tag(tool, "DevOps"):
        devops_updated += 1

conn.commit()
cur.close()
conn.close()

print(f"\n✅ Update complete!")
print(f"   BD tags added: {bd_updated}")
print(f"   DevOps tags added: {devops_updated}")
