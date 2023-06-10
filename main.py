from helpers.DiskMon import get_disk_used_percent,get_metriclist_for_instance
from helpers.MemoryMonitor import AsgMemoryMonitor
from helpers.CpuMon import AsgCPUMonitor,get_cpu_utilization
from jinja2 import Template
import os,yaml,subprocess,time,concurrent,boto3,sqlite3
from helpers.dbHandler import DbHandler
from helpers.MainLogger import setup_logger
logger = setup_logger()

start_time = time.perf_counter()
def startMemoryProcessing(instance_id,region_name,asg_name, Namespace,
                          MetricName):
    vmobj = AsgMemoryMonitor()
    memstatlist = vmobj._get_memory_usage(instance_id,region_name,asg_name,Namespace,MetricName,)
    return(memstatlist)

def startStorageProcessing(instance_id,region_name,asg_name, Namespace,
                          MetricName):

    storagestatlist = get_disk_used_percent(instance_id,region_name,asg_name,Namespace,MetricName,)
    return(storagestatlist)


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
    runninginstances = []
    tmphold = []
    with open(cpumonconfig, "r") as f:
        data = yaml.safe_load(f)
        futures = []
        for region_name in data['region_name']:
            print(f"Region {region_name}......")
            for asgname in data['ASG_NAME']:
                obje = AsgCPUMonitor(asgname, region_name, data["Namespace"], data["MetricName"])
                tmphold.append(obje._get_running_instances())

    for instancelist in tmphold:
        if instancelist is not None:
            for instance in instancelist:
                runninginstances.append(instance)
    del tmphold

    db_handler = DbHandler(dbfile)
    # get cpu utilization from the list of running instaces : here db_handler.close_connection() is done inside fxn
    cpudata = get_cpu_utilization(runninginstances)
    for d in cpudata:
        db_handler.insert_cpuusage_data(d)
        # db_handler.insert_cpuusage_data(d.get("instance_id"),d.get('instance_name'),d.get('public_ip'),d.get('private_ip'),d.get('cpu_usage'),
        #                                 d.get('asg_name'),d.get('region_name'))
        db_handler.close_connection()

    # -------------------------------------------------------------------------------------------------------------------------------------#
    with open(icingaconfigpath, "r") as f:
        icingadata = yaml.safe_load(f)
        icingahostfilepath = script_home + "/config/" + icingadata["icingahostfilepath"]
        hosttemplatepath = script_home + "/config/" + icingadata["hosttemplatepath"]
        truncate_file(icingahostfilepath)
    # Generation of the icinga host file happens here
    generate_host_file(icingahostfilepath, hosttemplatepath)
    # end
    # -------------------------------------------------------------------------------------------------------------------------------------#

    # Memory stat fetch starts here
    memory_monitor_config = script_home + "/config/monitor_memory.yaml"
    with open(memory_monitor_config, "r") as f:
        datafh = yaml.safe_load(f)

    memfuture=[]
    allmemdata=[]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for obz in cpudata:
            memfuture.append(executor.submit(startMemoryProcessing, obz["instance_id"],obz["region_name"],obz["asg_name"],datafh["Namespace"],datafh["Metricname"]))
        for future in concurrent.futures.as_completed(memfuture):
            allmemdata.append(future.result())  # this contains mem stat of all instances

    # allmemdata--> [{'instance_id': 'i-03450ec3cfc011cda', 'region_name': 'us-west-2', 'asg_name': 'MoodleCloudASG',
    # 'mem_used': 24.977146786393238}]
    db_handler_mem = DbHandler(dbfile)
    for md in allmemdata:
        if md["mem_used"] == 0:
            logger.warning(f"The {md['instance_id']} instance do not have CWAgent configured")
        db_handler_mem.insert_memusage_data(md)

    # --------------------------------------Disk Monitoring-----------------------------------------------------------------------------------------------#
    disk_monitor_config = script_home + "/config/monitor_disk.yaml"
    with open(disk_monitor_config, "r") as fh:
        datafh = yaml.safe_load(fh)

    sto_metric_name=datafh['Metricname']
    sto_asg_name=datafh['ASG_NAME']
    sto_namespace=datafh['Namespace']
    mount_point_list = []
    for mnt in datafh['mountpath']:
        mount_point_list.append(mnt)
    asg_list= []
    for asg in sto_asg_name:
        asg_list.append(asg)
    # cpu data sample [ {'instance_id': 'i-03450ec3cfc011cda', 'public_ip': '54.244.136.168', 'private_ip': '172.31.40.150',
    #   'instance_name': 'MoodleCloudASG_i-03450ec3cfc011cda', 'cpuusage': 0.5607262471355686,
    #   'asgname': 'MoodleCloudASG', 'region_name': 'us-west-2'},  ]
    all_instance_metric=[]
    for item in cpudata:
        all_instance_metric.append(get_metriclist_for_instance(item['instance_id'],item['region_name'],sto_namespace,sto_metric_name,item['asg_name'], mount_point_list))

    disk_data=[] #contains list obj of instances mountpoint data, such obj will be kept individually in fin_disk_data
    #[[{'instance_id': 'i-0c10cfcc8a0bec161', 'region_name': 'us-east-1', 'asg_name': 'northernAsg', 'disk_used': 34.8537171086833, 'mount_point': '/'}, {'instance_id': 'i-0c10cfcc8a0bec161', 'region_name': 'us-east-1', 'asg_name': 'northernAsg', 'disk_used': 20.11090761090761, 'mount_point': '/datadrive'}], [{'instance_id': 'i-04678cd0a99c43075', 'region_name': 'us-west-2', 'asg_name': 'Demoasg', 'disk_used': 32.71905589164275, 'mount_point': '/'}], False]
    dfuture=[] # hold the thread exec op
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for item in all_instance_metric:
            dfuture.append(executor.submit(get_disk_used_percent,item['instance_id'],item['region_name'],item['asg_name'],item['metric_name'],item['namespace'],item['DimensionsData']))
            #disk_data.append(get_disk_used_percent(item['instance_id'],item['region_name'],item['asg_name'],item['metric_name'],item['namespace'],item['DimensionsData']))
        for future in concurrent.futures.as_completed(dfuture):
            disk_data.append(future.result())


    fin_disk_data=[]

    for lst in disk_data:
        if lst is False:
            continue
        else:
            for instancedata in lst:
                fin_disk_data.append(instancedata)

    print(f"\n\n---disk_data---{fin_disk_data}")
    db_handler_disk = DbHandler(dbfile)
    # fin_disk_data > [{'instance_id': 'i-04678cd0a99c43075', 'region_name': 'us-west-2', 'asg_name': 'Demoasg', 'disk_used': 32.71905589164275, 'mount_point': '/'}, {'instance_id': 'i-0c10cfcc8a0bec161', 'region_name': 'us-east-1', 'asg_name': 'northernAsg', 'disk_used': 34.8537171086833, 'mount_point': '/'}, {'instance_id': 'i-0c10cfcc8a0bec161', 'region_name': 'us-east-1',
    # 'asg_name': 'northernAsg', 'disk_used': 20.11090761090761, 'mount_point': '/datadrive'}]
    for dat in fin_disk_data:
        db_handler_disk.insert_diskusage_data(dat)

    #(data["instance_id"], data["DiskUsage"], data["MountPoint"],data["asg_name"],data["region_name"]))



    end_time = time.perf_counter()
    execution_time = end_time - start_time
    print(f"Total Elapsed time: {execution_time:.6f} Seconds")

if __name__ == "__main__":
    main()


#i-04678cd0a99c43075 --demoasg