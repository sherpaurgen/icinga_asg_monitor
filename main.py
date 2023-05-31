from DiskMon import AsgDiskMonitor
from MemoryMonitor import AsgMemoryMonitor
from CpuMon import AsgCPUMonitor
from jinja2 import Template
import subprocess
import yaml
import os
from dbHandler import DbHandler

def startMemoryProcessing(ASG_NAME, region_name, Namespace,
                          MetricName,hosttemplatepath,
                          icingahostfilepath,db_handler):
    adm1 = AsgMemoryMonitor(asg_name=ASG_NAME, region_name=region_name, namespace=Namespace,
                          metric_name=MetricName, hosttemplatepath=hosttemplatepath,
                          icingahostfilepath=icingahostfilepath)
    if adm1.verify_asg() is False:
        return
    metric_list_with_asgec2=adm1._get_metric_instanceid_from_asg()
    # print(metric_list_with_asgec2)
    runningec2=adm1._get_running_ec2(metric_list_with_asgec2)
    if runningec2 is False:
        return
    # Preparing list for ec2 that are powered on/running i-0f854388d312bc919
    running_ec2_metric_list = []

    for id in runningec2:
        for dim in metric_list_with_asgec2:
            if dim["Dimensions"][0]["Value"] == id:
                running_ec2_metric_list.append(dim)

    for ecm in running_ec2_metric_list:
        adm1._get_memory_usage(ecm,db_handler)


def startDiskProcessing(ASG_NAME, region_name, mountpath, Namespace,
                    MetricName, hosttemplatepath,
                    icingahostfilepath, db_handler, hostSetVar):
    adm1 = AsgDiskMonitor(asg_name=ASG_NAME, region_name=region_name, mountpath=mountpath, namespace=Namespace,
                          metric_name=MetricName, hosttemplatepath=hosttemplatepath,
                          icingahostfilepath=icingahostfilepath)
    if adm1.verify_asg() is False:
        return

    ec2_ASG = adm1._get_ec2_from_asg()

    if ec2_ASG is False:
        return
    asgInstanceId = []
    ec2ListRunning = []
    for ec2cwdata in ec2_ASG:
        for item in ec2cwdata["Dimensions"]:
            if item['Name'] == 'InstanceId':
                asgInstanceId.append(item['Value'])
                break
            else:
                continue
    if len(asgInstanceId) > 0:
        # print('------asgInstanceId-------')
        # print(asgInstanceId)
        for instanceid in asgInstanceId:
            instanceData = adm1._get_ec2_detail(instanceid)
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_instance_status.html
            # 16 is equivalent to running state
            if instanceData and instanceData['state'] == 16:
                ec2ListRunning.append(instanceData['instance_id'])
                hostSetVar.add((instanceData['instance_name'],
                                instanceData['pub_ip'], instanceData['instance_id'], ASG_NAME, region_name))

                # adm1._generate_host_file(instanceData['instance_name'],
                #                          instanceData['pub_ip'], instanceData['instance_id'])
    # Writing to ASG_EC2_Host.conf
    if not ec2_ASG or len(ec2ListRunning) < 1:
        adm1.logger.warning("Empty ec2_ASG OR ec2ListRunning list")
    else:
        for instance in ec2ListRunning:
            for ec2metric in ec2_ASG:
                for data in ec2metric['Dimensions']:
                    if data.get('Name') == 'InstanceId':
                        instanceid = data.get('Value')
                        if instanceid == instance:
                            adm1._get_disk_used_percent(ec2metric, db_handler)
                    else:
                        continue
    ec2ListRunning.clear()
    adm1._reloadIcinga()


def truncate_file(icingahostfilepath):
    with open(icingahostfilepath, 'w') as file:
        file.truncate()
    subprocess.call(['chmod', '0755', icingahostfilepath])


def generate_host_file(icingahostfilepath, hosttemplatepath, instance_name, pub_ip, instance_id, asg_name, region_name):
    # icingahostfilepath,hosttemplatepath, instance_name, pub_ip, instance_id,asg_name,region_name
    with open(hosttemplatepath, 'r') as file:
        template_content = file.read()

    template = Template(template_content)
    rendered_template = template.render(hostname=instance_name, address=pub_ip, asg_name=asg_name,
                                        instance_id=instance_id)
    with open(icingahostfilepath, 'a') as output_file:
        output_file.write(rendered_template)


def main():
    hostSetVar = set()
    icingahostfilepath = ""
    hosttemplatepath = ""

    script_home = os.path.dirname(os.path.abspath(__file__))
    diskmntconfig = script_home + "/monitor_disk.yaml"
    dbfile = script_home + "/icinga.db"
    # setupLocalDb(dbfile)
    db_handler = DbHandler(dbfile)

    # Loading the monitor_disk.yaml data
    with open(diskmntconfig, "r") as f:
        data = yaml.safe_load(f)
        mountpaths = data["mountpath"]
        truncate_file(data["icingahostfilepath"])
        icingahostfilepath = data["icingahostfilepath"]
        hosttemplatepath = data["hosttemplatepath"]
        for region_name in data['region_name']:
            for asgname in data["ASG_NAME"]:
                for path in mountpaths:
                    print("Gettings stats for mount Path:", path)
                    startDiskProcessing(asgname, region_name, path, data["Namespace"],
                                    data["MetricName"], data["hosttemplatepath"],
                                    data["icingahostfilepath"], db_handler, hostSetVar)
    if len(hostSetVar) > 0:
        for item in hostSetVar:
            # hostSetVar.add((instanceData['instance_name'],instanceData['pub_ip'], instanceData['instance_id'],ASG_NAME,region_name))
            generate_host_file(icingahostfilepath, hosttemplatepath, item[0], item[1], item[2], item[3], item[4])
    db_handler.close_connection()

    # #  #  Memory monitor start # # #
    memory_monitor_config = script_home + "/monitor_memory.yaml"
    db_handler = DbHandler(dbfile)
    # # Loading the monitor_disk.yaml data
    with open(memory_monitor_config, "r") as f:
        data = yaml.safe_load(f)
        for region_name in data['region_name']:
            for asgname in data["ASG_NAME"]:
                startMemoryProcessing(asgname, region_name, data["Namespace"], data["Metricname"],data["hosttemplatepath"], data["icingahostfilepath"], db_handler)

    db_handler.close_connection()

    # # # # Cpu Monitor starts from here
    cpumonconfig = script_home + "/monitor_cpu.yaml"

    with open(cpumonconfig, "r") as f:
        data = yaml.safe_load(f)
        for region_name in data['region_name']:
            for asgname in data['ASG_NAME']:
                obj = AsgCPUMonitor(asgname, region_name, data["Namespace"], data["MetricName"])
                db_handler = DbHandler(dbfile)
                runninginstances = obj._get_running_instances()
                if runninginstances is False:
                    continue
                else:
                    obj._get_cpu_utilization(runninginstances, db_handler)
    db_handler.close_connection()


if __name__ == "__main__":
    main()