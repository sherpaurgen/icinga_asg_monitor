#!/monitoringScripts/VENVT/bin/python
import sys
import sqlite3
from config import sqlitefilepath
conn = sqlite3.connect(sqlitefilepath)
cursor = conn.cursor()

instanceid=sys.argv[1]

# Define the query to select the latest record -only1 row
query = "SELECT cpu_usage FROM cpu_usage WHERE instance_id = ? ORDER BY id DESC LIMIT 1;"
rows=cursor.execute(query, (instanceid,))
for row in rows:
    cpuusage=row[0]

if cpuusage >= 90:
    print(f"CRITICAL - cpu usage is above threshold {cpuusage}")
    sys.exit(2)
elif cpuusage >= 75:
    print(f"WARNING - cpu usage is approaching threshold {cpuusage}")
    sys.exit(1)
else:
    print(f"OK - cpu usage is within limits {cpuusage}")
    sys.exit(0)

