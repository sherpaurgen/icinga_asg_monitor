#!/monitoringScripts/VENVT/bin/python
import sys
import sqlite3
#conn = sqlite3.connect('/monitoringScripts/code/icinga.db')
conn = sqlite3.connect('/Users/ush/PycharmProjects/SHV/icinga.db')
cursor = conn.cursor()
instanceid=sys.argv[1]
mountpoint=sys.argv[2]
# Define the query to select the latest record
query = "SELECT DiskUsage FROM disk_usage WHERE instance_id = ? and MountPoint = ? ORDER BY id DESC LIMIT 1;"
cursor.execute(query, (instanceid,mountpoint,))
diskusageTuple = cursor.fetchone()
if diskusageTuple is None:
    diskusage=0
else:
    diskusage=diskusageTuple[0]


if diskusage >= 90:
    print(f"CRITICAL - Disk usage is above threshold {diskusage}")
    sys.exit(2)
elif diskusage == 0:
    print(f"OK - Mountpoint not found {diskusage}")
    sys.exit(0)
elif diskusage >= 75:
    print(f"WARNING - Disk usage is approaching threshold {diskusage}")
    sys.exit(1)
else:
    print(f"OK - Disk usage is within limits {diskusage}")
    sys.exit(0)