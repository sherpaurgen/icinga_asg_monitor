from helpers.DiskMon import AsgDiskMonitor
from helpers.MemoryMonitor import AsgMemoryMonitor
from helpers.CpuMon import AsgCPUMonitor
from jinja2 import Template
from helpers.MainLogger import setup_logger
import os,yaml,subprocess,time,concurrent,boto3,sqlite3
from helpers.dbHandler import DbHandler
from datetime import datetime, timedelta

logger = setup_logger()

start_time = time.perf_counter()
def startMemoryProcessing(instance_id,region_name,asg_name, Namespace,
                          MetricName):
    vmobj = AsgMemoryMonitor()
    memstatlist = vmobj._get_memory_usage(instance_id,region_name,asg_name,Namespace,MetricName,)
    return(memstatlist)

def get_ec2_ASG_metriclist(ASG_NAME, region_name, mountpath, Namespace,
                    MetricName, hosttemplatepath,
                    icingahostfilepath, db_handler, hostSetVar):
    adm1 = AsgDiskMonitor(asg_name=ASG_NAME, region_name=region_name, mountpath=mountpath, namespace=Namespace,
                          metric_name=MetricName, hosttemplatepath=hosttemplatepath,icingahostfilepath=icingahostfilepath)
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

def get_cpu_utilization(running_instances):
    ft = []
    allcpudata=[]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for instance in running_instances:
            ft.append(executor.submit(get_metric_statistics_of_instance_savetolist,instance))
        for future in concurrent.futures.as_completed(ft):
            allcpudata.append(future.result())
    return allcpudata

def get_metric_statistics_of_instance_savetolist(instancerunning):
    try:
        cw_cli = boto3.client('cloudwatch', region_name=instancerunning["region_name"])
        instance_id = instancerunning['instance_id']
        dimensions = [{'Name': 'InstanceId', 'Value': instance_id }]
        response = cw_cli.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=dimensions,
            StartTime=datetime.utcnow() - timedelta(seconds=600),
            EndTime=datetime.utcnow(),
            Period=300,
            Statistics=['Average']
        )

        if len(response["Datapoints"]) == 0:
            print(f"Datapoint empty Region:"+instancerunning["region_name"]+instancerunning["instance_id"]+instancerunning["asg_name"])
            print(response)
            print("Make sure cloudwatch agent is installed or check the CW logs")

        if len(response["Datapoints"])>0:
            cpuusage = response["Datapoints"][0].get("Average", 0)
        else:
            return
        # Extract the public ip of running instance from response.
        try:
            public_ip = instancerunning["public_ip"]
        except Exception as e:
            public_ip = instancerunning["private_ip"]
            logger.warning("_get_metric_statistics_of_instance_savetodb : public ip not found, Using private ip for " + instance_id +str(e))

        data = { "instance_id": instance_id, "public_ip": public_ip, "private_ip": instancerunning["private_ip"],
                 "instance_name": instancerunning["instance_name"], "cpuusage": cpuusage,
                "asgname": instancerunning["asg_name"], "region_name": instancerunning['region_name']}
        return data

    except Exception as e:
        logger.warning("_get_metric_statistics_of_instance_savetodb: Exception: " + str(e))
        return

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
                    obje = AsgCPUMonitor(asgname, region_name, data["Namespace"], data["MetricName"])
                    futures.append(executor.submit(obje._get_running_instances))
    # fetch completed jobs
    for fut in concurrent.futures.as_completed(futures):
        if fut.result() is not None:
            runninginstances=fut.result()

    db_handler = DbHandler(dbfile)
    # get cpu utilization from the list of running instaces : here db_handler.close_connection() is done inside fxn
    cpudata = get_cpu_utilization(runninginstances)

    for d in cpudata:
        db_handler.insert_cpuusage_data(d)
        # db_handler.insert_cpuusage_data(d.get("instance_id"),d.get('instance_name'),d.get('public_ip'),d.get('private_ip'),d.get('cpu_usage'),
        #                                 d.get('asg_name'),d.get('region_name'))
        db_handler.close_connection()
    # cpu data sample [{'instance_id': 'i-03450ec3cfc011cda', 'public_ip': '54.244.136.168', 'private_ip': '172.31.40.150',
    #   'instance_name': 'MoodleCloudASG_i-03450ec3cfc011cda', 'cpuusage': 0.5607262471355686,
    #   'asgname': 'MoodleCloudASG', 'region_name': 'us-west-2'},]

    with open(icingaconfigpath, "r") as f:
        icingadata = yaml.safe_load(f)
        icingahostfilepath = script_home + "/config/" + icingadata["icingahostfilepath"]
        hosttemplatepath = script_home + "/config/" + icingadata["hosttemplatepath"]
        truncate_file(icingahostfilepath)
    # Generating the icinga host file happens here
    generate_host_file(icingahostfilepath, hosttemplatepath)
    # end

    #Memory stat fetch starts here
    memory_monitor_config = script_home + "/config/monitor_memory.yaml"
    with open(memory_monitor_config, "r") as f:
        datafh = yaml.safe_load(f)

    memfuture=[]
    allmemdata=[]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for obz in cpudata:
            memfuture.append(executor.submit(startMemoryProcessing, obz["instance_id"],obz["region_name"],obz["asgname"],datafh["Namespace"],datafh["Metricname"]))
        for future in concurrent.futures.as_completed(memfuture):
            allmemdata.append(future.result())  # this contains mem stat of all instances

    #allmemdata--> [{'instance_id': 'i-03450ec3cfc011cda', 'region_name': 'us-west-2', 'asg_name': 'MoodleCloudASG', 'mem_used': 24.977146786393238}]
    db_handler_mem = DbHandler(dbfile)
    for md in allmemdata:
        if md["mem_used"] == 0:
            logger.warning(f"The {md['instance_id']} instance do not have CWAgent configured")
        db_handler_mem.insert_memusage_data(md)
    db_handler_mem.close_connection()
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    print(f"Total Elapsed time: {execution_time:.6f} seconds")
if __name__ == "__main__":
    main()


#i-04678cd0a99c43075 --demoasg