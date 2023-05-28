import boto3
import logging
from jinja2 import Template
from datetime import datetime, timedelta
import subprocess
import yaml
import os
from dbHandler import DbHandler

class AsgDiskMonitor:
    def __init__(self, asg_name, region_name, mountpath,namespace ,metric_name, hosttemplatepath, icingahostfilepath):
        self.asg_name = asg_name
        self.region_name = region_name
        self.mountpath = mountpath
        self.namespace = namespace
        self.metric_name = metric_name
        self.logger = self._create_logger()
        self.hosttemplatepath = hosttemplatepath
        self.icingahostfilepath = icingahostfilepath


    def _create_logger(self):

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s",'%Y-%m-%d %H:%M:%S')
        file_handler = logging.FileHandler("/tmp/custom_ec2_info_fetcher.log")
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        return logger

    def _get_ec2_from_asg(self):
        # verifying if ASG is has at least 1 instance
        cw_client_asg = boto3.client('autoscaling', region_name=self.region_name)
        response = cw_client_asg.describe_auto_scaling_groups(AutoScalingGroupNames=[self.asg_name])
        # return false if the asg name is not found
        if not response["AutoScalingGroups"]:
            return (False)
        ASG_EC2S = []
        cloudwatch_client = boto3.client('cloudwatch', region_name=self.region_name)
        resp = cloudwatch_client.list_metrics(
            Namespace=self.namespace,
            MetricName=self.metric_name
        )
        if "Metrics" in resp:
            self.logger.warning("Metrics found in the GET request")
            for metric in resp["Metrics"]:
                if metric["Namespace"] == self.namespace and metric["MetricName"] == self.metric_name:
                    if {'Value': self.asg_name, 'Name': 'AutoScalingGroupName'} in metric["Dimensions"] and {'Name': 'path', 'Value': self.mountpath} in metric["Dimensions"]:
                        ASG_EC2S.append(metric)
                else:
                    continue

            return (ASG_EC2S)
        else:
            self.logger.warning("Err _get_ec2_from_asg: Metrics not found. Please check response obj")

    def _get_disk_used_percent(self, ec2metric,db_handler):
        try:
            start_time = datetime.utcnow() - timedelta(minutes=5)
            end_time = datetime.utcnow()
            period = 300
            cloudwatch = boto3.client('cloudwatch', region_name=self.region_name)
            res = cloudwatch.get_metric_statistics(
                Namespace=ec2metric['Namespace'],
                MetricName=ec2metric['MetricName'],
                Dimensions=ec2metric['Dimensions'],
                StartTime=start_time,
                EndTime=end_time,
                Period=period,
                Statistics=['Average']
            )
            instance_id = ""
            mount_point= ""
            for item in ec2metric['Dimensions']:
                if item.get('Name') == 'InstanceId':
                    instance_id = item.get('Value')
                if item.get('Name') == 'path':
                    mount_point=item.get('Value')
            disk_usage = 0
            for point in res['Datapoints']:
                if 'Average' in point:
                    disk_usage = point['Average']
                    break
            data = {"instance_id": instance_id, "DiskUsage": disk_usage,"MountPoint": mount_point,"asg_name":self.asg_name,"region_name":self.region_name }
            print("data from"+self.asg_name)
            print(data)
            db_handler.insert_diskusage_data(data)
            # with open("/tmp/" + instance_id + ".json", 'w') as fh:
            #     json.dump(data, fh)
        except Exception as e:
            self.logger.warning("_get_disk_used_percent Failed: " + str(e))

    def _get_ec2_detail(self,instance_id):
        ec2_client = boto3.client('ec2', self.region_name)
        instance_id = instance_id
        try:
            response = ec2_client.describe_instances(InstanceIds=[instance_id])
            # print("_get_ec2_detail  : " + str(instance_id))
            # print("From _get_ec2_detail: " + str(response))

        except Exception as e:
            self.logger.warning("_get_ec2_detail Failed :")
            self.logger.warning(str(e))
            return (False)

        instance_name = ''
        if len(response['Reservations']) < 1:
            return (False)
        try:
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    public_ip = instance.get('PublicIpAddress', 'N/A')
                    dns_name = instance.get('PublicDnsName', 'N/A')
                    state = instance['State']['Code']
                    # Get the instance name if its set
                    for tag in instance['Tags']:
                        if tag['Key'] == 'Name':
                            instance_name = tag.get('Value', 'NoHostname')
                            if len(instance_name) < 1:
                                instance_name = 'No name specified'
                            break
                        else:
                            instance_name = 'No name specified'
                return (
                    {"instance_id": instance_id, "pub_ip": public_ip, "dns_name": dns_name,
                     "instance_name": instance_name,
                     "state": state})
        except Exception as e:
            self.logger.warning("_get_ec2_detail Error:" + str(e))

    def _generate_host_file(self, instance_name, pub_ip, instance_id):
        with open(self.hosttemplatepath, 'r') as file:
            template_content = file.read()

        template = Template(template_content)
        rendered_template = template.render(hostname=instance_name, address=pub_ip, asg_name=self.asg_name,
                                            instance_id=instance_id)
        with open(self.icingahostfilepath, 'a') as output_file:
            output_file.write(rendered_template)

    def _truncate_file(self):
        with open(self.icingahostfilepath, 'w') as file:
            file.truncate()
        subprocess.call(['chmod', '0755', self.icingahostfilepath])

    def _reloadIcinga(self):
        # command1 = "/usr/sbin/icinga2 daemon -C"
        command1 = "echo cmd1"
        try:
            subprocess.run(command1, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"reloadIcinga: Command '{command1}' failed with exit code {e.returncode}")
        else:
            # Run the second command if the first command succeeded
            # command2 = "sudo systemctl reload icinga2"
            command2 = "echo cmd2"
            try:
                subprocess.run(command2, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                self.logger.warning(f"reloadIcinga: Command '{command2}' failed with exit code {e.returncode}")
            else:
                self.logger.warning("Icinga2 Reloaded Successfully")

    def verify_asg(self):
        cw_client_asg = boto3.client('autoscaling', region_name=self.region_name)
        response = cw_client_asg.describe_auto_scaling_groups(AutoScalingGroupNames=[self.asg_name])
        # return false if the asg name is not found
        if not response["AutoScalingGroups"]:
            return (False)
        else:
            return (True)

def startProcessing(ASG_NAME, region_name, mountpath, Namespace,
                          MetricName,hosttemplatepath,
                          icingahostfilepath,db_handler):
    adm1 = AsgDiskMonitor(asg_name=ASG_NAME, region_name=region_name, mountpath=mountpath, namespace=Namespace,
                          metric_name=MetricName, hosttemplatepath=hosttemplatepath,
                          icingahostfilepath=icingahostfilepath)
    if adm1.verify_asg() is False:
        return
    adm1._truncate_file()
    ec2_ASG = adm1._get_ec2_from_asg()
    print("ec2_ASG list from startProcessing:")
    print(ec2_ASG)
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
        for instanceid in asgInstanceId:
            instanceData = adm1._get_ec2_detail(instanceid)
            print("CheckInstanceData :" + str(instanceData))
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_instance_status.html
            # 16 is equivalent to running state
            if instanceData and instanceData['state'] == 16:
                ec2ListRunning.append(instanceData['instance_id'])
                adm1._generate_host_file(instanceData['instance_name'],
                                         instanceData['pub_ip'], instanceData['instance_id'])
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
                            adm1._get_disk_used_percent(ec2metric,db_handler)
                    else:
                        continue
    ec2ListRunning.clear()
    adm1._reloadIcinga()



def main():
    script_home = os.path.dirname(os.path.abspath(__file__))
    diskmntconfig = script_home+"/monitor_disk.yaml"
    dbfile = script_home+"/monitoring.db"
    # setupLocalDb(dbfile)
    db_handler=DbHandler(dbfile)

    # Loading the monitor_disk.yaml data
    with open(diskmntconfig, "r") as f:
        data = yaml.safe_load(f)
        mountpaths = data["mountpath"]
        # return false if the asg name is not found
        for asgname in data["ASG_NAME"]:
            for path in mountpaths:
                print("Mount Path:", path)
                startProcessing(asgname, data["region_name"], path, data["Namespace"],
                              data["MetricName"], data["hosttemplatepath"],
                             data["icingahostfilepath"],db_handler)

    db_handler.close_connection()


if __name__ == "__main__":
    main()