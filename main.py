from helpers.DiskMon import AsgDiskMonitor
from helpers.MemoryMonitor import AsgMemoryMonitor
from helpers.CpuMon import AsgCPUMonitor
from jinja2 import Template
import subprocess
import yaml
import os
from helpers.dbHandler import DbHandler
import time
import concurrent
import boto3
import sqlite3

start_time = time.perf_counter()
def startMemoryProcessing(instance_id,region_name,asg_name, Namespace,
                          MetricName,db_handler):
    vmobj = AsgMemoryMonitor()
    vmobj._get_memory_usage(instance_id,region_name,asg_name,Namespace,MetricName,db_handler)


def get_ec2_ASG_metriclist(ASG_NAME, region_name, mountpath, Namespace,
                    MetricName, hosttemplatepath,
                    icingahostfilepath, db_handler, hostSetVar):
    adm1 = AsgDiskMonitor(asg_name=ASG_NAME, region_name=region_name, mountpath=mountpath, namespace=Namespace,
                          metric_name=MetricName, hosttemplatepath=hosttemplatepath,icingahostfilepath=icingahostfilepath)
    print("details...")
    print(ASG_NAME, region_name, mountpath, Namespace,
                    MetricName, hosttemplatepath,
                    icingahostfilepath)

    #adm1._get_disk_used_percent(ec2_ASG_metriclist, db_handler)


def truncate_file(icingahostfilepath):
    with open(icingahostfilepath, 'w') as file:
        file.truncate()
    subprocess.call(['chmod', '0644', icingahostfilepath])


def generate_host_file(icingahostfilepath, hosttemplatepath):
    con = sqlite3.connect('icinga.db')
    cursor = con.cursor()
    cursor.execute('SELECT * FROM cpu_usage')
    rows = cursor.fetchall()
    with open(hosttemplatepath, 'r') as file:
        template_content = file.read()
    template = Template(template_content)
    for row in rows:
        rendered_template = template.render(hostname=row[2], address=row[3], asg_name=row[6], instance_id=row[1])
        with open(icingahostfilepath, 'a') as output_file:
            output_file.write(rendered_template)
        #(56, 'i-04678cd0a99c43075', 'Demoasg_i-04678cd0a99c43075', '52.39.213.223', '172.31.39.118', 0.0989988876529518, 'Demoasg', 'us-west-2', '2023-06-06 09:15:28')
    cursor.close()
    con.close()

    # # icingahostfilepath,hosttemplatepath, instance_name, pub_ip, instance_id,asg_name,region_name

def reloadIcinga(self):
    command1 = "/usr/sbin/icinga2 daemon -C > /dev/null 2>&1"
    # command1 = "echo"
    try:
        subprocess.run(command1, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"reloadIcinga: Command '{command1}' failed with exit code {e.returncode}")
    else:
        # Run the second command if the first command succeeded
        command2 = "sudo systemctl reload icinga2"
        # command2 = "echo"
        try:
            subprocess.run(command2, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"reloadIcinga: Command '{command2}' failed with exit code {e.returncode}")
        else:
            print("Icinga2 Reloaded Successfully")

def ListAsgInRegion(region_name):
    cw_client_asg = boto3.client('autoscaling', region_name=region_name)
    response = cw_client_asg.describe_auto_scaling_groups()
    print(response)

def main():
    hostSetVar = set()
    script_home = os.path.dirname(os.path.abspath(__file__))
    dbfile = script_home + "/icinga.db"
    # setupLocalDb(dbfile)
    db_handler = DbHandler(dbfile)
    db_handler.truncate_table()

    # Start fetching cpu info
    icingaconfigpath = script_home + "/config/icinga_config.yaml"
    cpumonconfig = script_home + "/config/monitor_cpu.yaml"
    runninginstances=[]
    with open(cpumonconfig, "r") as f:
        data = yaml.safe_load(f)
        futures = []
        for region_name in data['region_name']:
            print(f"Region {region_name}......")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for asgname in data['ASG_NAME']:
                    obj = AsgCPUMonitor(asgname, region_name, data["Namespace"], data["MetricName"])
                    db_handler = DbHandler(dbfile)
                    futures.append(executor.submit(obj._get_running_instances,runninginstances))
                for fut in concurrent.futures.as_completed(futures):
                    pass
    print("RUNNING ......")
    print(runninginstances)
    print()
    # get cpu utilization from the list of running instaces : here db_handler.close_connection() is done inside fxn
    cpudata=obj._get_cpu_utilization(runninginstances)
    for d in cpudata:
        db_handler.insert_cpuusage_data(d)
        # db_handler.insert_cpuusage_data(d.get("instance_id"),d.get('instance_name'),d.get('public_ip'),d.get('private_ip'),d.get('cpu_usage'),
        #                                 d.get('asg_name'),d.get('region_name'))
        db_handler.close_connection()

    # with open(icingaconfigpath, "r") as f:
    #     icingadata = yaml.safe_load(f)
    #     icingahostfilepath = script_home + "/config/" + icingadata["icingahostfilepath"]
    #     hosttemplatepath = script_home + "/config/" + icingadata["hosttemplatepath"]
    #     truncate_file(icingahostfilepath)
    # # Generating the icinga host file happens here
    # generate_host_file(icingahostfilepath, hosttemplatepath)
    # end

    #Memory monitor starts here
    memory_monitor_config = script_home + "/config/monitor_memory.yaml"

    with open(memory_monitor_config, "r") as f:
        data = yaml.safe_load(f)

    #get
    db_handler_mem = DbHandler(dbfile)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        con = sqlite3.connect('icinga.db')
        cursor = con.cursor()
        cursor.execute('SELECT instance_id,region_name,asg_name  FROM cpu_usage')
        rows = cursor.fetchall()
        for row in rows:
            meminstanceobj = startMemoryProcessing(row[0], row[1],row[2], data["Namespace"], data["Metricname"],db_handler_mem)






    db_handler_mem.close_connection()
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    print(f"Total Execution time: {execution_time:.6f} seconds")
if __name__ == "__main__":
    main()


#i-04678cd0a99c43075 --demoasg