#!/code/VENV/bin/python
import sys
import sqlite3

conn = sqlite3.connect('icinga.db')
cursor = conn.cursor()

instanceid=sys.argv[1]

# Define the query to select the latest record
query = "SELECT cpuusage FROM cpu_usage WHERE instance_id = ? ORDER BY id DESC LIMIT 1;"
cursor.execute(query, (instanceid,))
cpuusage = cursor.fetchone()[0]


if cpuusage >= 90:
    print(f"CRITICAL - cpuory usage is above threshold {cpuusage}")
    sys.exit(2)
elif cpuusage >= 75:
    print(f"WARNING - cpuory usage is approaching threshold {cpuusage}")
    sys.exit(1)
else:
    print(f"OK - cpuory usage is within limits {cpuusage}")
    sys.exit(0)

