#!/monitoringScripts/VENVT/bin/python
import sys
import sqlite3

conn = sqlite3.connect('/monitoringScripts/code/icinga.db')
cursor = conn.cursor()

instanceid=sys.argv[1]

# Define the query to select the latest record -only1 row
query = "SELECT cpuusage FROM cpu_usage WHERE instance_id = ? ORDER BY id DESC LIMIT 1;"
cpuusageTuple=cursor.execute(query, (instanceid,))
if cpuusageTuple is None:
    cpuusage=0
else:
    cpuusage = cpuusageTuple[0]


if cpuusage >= 90:
    print(f"CRITICAL - cpuory usage is above threshold {cpuusage}")
    sys.exit(2)
elif cpuusage >= 75:
    print(f"WARNING - cpuory usage is approaching threshold {cpuusage}")
    sys.exit(1)
else:
    print(f"OK - cpuory usage is within limits {cpuusage}")
    sys.exit(0)

