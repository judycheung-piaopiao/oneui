"""
Update tags for tools
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

# Define tags for each category
trader_tools = [
    "RMS UI",
    "Charges UI",
    "AG Trades DB",
    "HFT Cloud DB Management and Subscriptions",
    "AG-config Management System",
    "CryptoVerse",
    "Holidays",
    "Corporate Action as Service",
    "Trading Hours",
    "Startegy Monitor",
    "MIS Dashboard",
    "Auto Binary Deployer",
    "Grafana",
    "Calling Bot"
]

# Update trader tools
updated = 0
for tool_name in trader_tools:
    cur.execute("""
        UPDATE tools 
        SET tags = %s 
        WHERE name = %s
    """, (Json(["Trader"]), tool_name))
    
    if cur.rowcount > 0:
        updated += 1
        print(f"✅ Updated: {tool_name} -> [Trader]")
    else:
        print(f"⚠️  Tool not found: {tool_name}")

conn.commit()
cur.close()
conn.close()

print(f"\n✅ Update complete! Updated {updated} tools")
