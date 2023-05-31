# #!/code/VENV/bin/python
import json
import sys

instance_id=sys.argv[1]
filename="/tmp/"+instance_id+".json"
with open(filename,"r") as fh:
    jsonData=fh.read()

usage=json.loads(jsonData)
diskusage=usage['DiskUsage']
if diskusage >= 90:
    print(f"CRITICAL - Disk usage is above threshold {diskusage}")
    sys.exit(2)
elif diskusage >= 75:
    print(f"WARNING - Disk usage is approaching threshold {diskusage}")
    sys.exit(1)
else:
    print(f"OK - Disk usage is within limits {diskusage}")
    sys.exit(0)
