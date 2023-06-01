###  Python program to fetch memory, cpu and disk-mountpoints using Boto3 & aws services

- Install pkgs from requirements.txt
- Activate virtual enviroment
- to run scripts 
- python3 main.py

Edit the params below in `monitor_disk.yaml`

For example:
```
icingahostfilepath: '/etc/icinga2/conf.d/ASG_EC2_Host.conf'
hosttemplatepath: '/path/to/ec2host.j2'
```
_ASG_EC2_Host.conf_ this files contains the host objects(instances found in ASG across regions)

### Reference for icinga configs
_icinga services.conf_
```json
apply Service "ec2_disk_usage_service_root" {
  import "generic-service"
  check_command = "check_ec2_disk_usage_on_rootPartition"
  vars.arg1 = host.vars.instance_id
  vars.arg2 = "/"
  assign where host.vars.asg_name == "AsgUsh"
}
```
_commands.conf_
```json
object CheckCommand "check_ec2_disk_usage_on_rootPartition" {
  import "plugin-check-command"
  command = ["/code/monit/checkDiskUsage.py","$arg1$","$arg2$"]
  timeout = 60s
}
```
Data fetched from cloudwatch is stored in SQLite db - **_icinga.db_**
Use sqlite3 command and query the 3 tables to see if fetched data is available.

