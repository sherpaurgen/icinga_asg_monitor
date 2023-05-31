import sys
import sqlite3
conn = sqlite3.connect('/code/monit/icinga.db')
cursor = conn.cursor()
instanceid=sys.argv[1]
mountpoint=sys.argv[2]
# Define the query to select the latest record
query = "SELECT DiskUsage FROM disk_usage WHERE instance_id = ? and MountPoint = ? ORDER BY id DESC LIMIT 1;"
cursor.execute(query, (instanceid,mountpoint))
diskusagetuple = cursor.fetchone()
diskusage=diskusagetuple[0]

if diskusage >= 90:
    print(f"CRITICAL - Disk usage is above threshold {diskusage}")
    sys.exit(2)
elif diskusage >= 75:
    print(f"WARNING - Disk usage is approaching threshold {diskusage}")
    sys.exit(1)
else:
    print(f"OK - Disk usage is within limits {diskusage}")
    sys.exit(0)