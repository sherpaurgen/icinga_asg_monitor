#!/monitoringScripts/VENVT/bin/python
import sys
import sqlite3

conn = sqlite3.connect('/monitoringScripts/code/icinga.db')
cursor = conn.cursor()

instanceid=sys.argv[1]

# Define the query to select the latest record
query = "SELECT memusage FROM mem_usage WHERE instance_id = ? ORDER BY id DESC LIMIT 1;"
memusageTuple = cursor.execute(query, (instanceid,))
if memusageTuple is None:
    memusage=0
else:
    memusage = memusageTuple[0]

if memusage >= 90:
    print(f"CRITICAL - Memory usage is above threshold {memusage}")
    sys.exit(2)
elif memusage >= 75:
    print(f"WARNING - Memory usage is approaching threshold {memusage}")
    sys.exit(1)
else:
    print(f"OK - Memory usage is within limits {memusage}")
    sys.exit(0)