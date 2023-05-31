#!/monitoringScripts/VENVT/bin/python
import boto3
import logging
from jinja2 import Template
from datetime import datetime, timedelta
import subprocess
import yaml
import os
from dbHandler import DbHandler

class AsgMemoryMonitor:
    def __init__(self, asg_name, region_name,namespace ,metric_name, hosttemplatepath, icingahostfilepath):
        self.asg_name = asg_name
        self.region_name = region_name
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

    def verify_asg(self):
        cw_client_asg = boto3.client('autoscaling', region_name=self.region_name)
        response = cw_client_asg.describe_auto_scaling_groups(AutoScalingGroupNames=[self.asg_name])
        # return false if the asg name is not found
        if not response["AutoScalingGroups"]:
            self.logger.warning("Error in verify_asg: ASG not found please check asg name exist in monitor_memory.yaml")
            return (False)
        else:
            return (True)

    def _get_metric_instanceid_from_asg(self):

        ASG_EC2S = []
        cloudwatch_client = boto3.client('cloudwatch', region_name=self.region_name)
        resp = cloudwatch_client.list_metrics(
            Namespace=self.namespace,
            MetricName=self.metric_name
        )

        if "Metrics" in resp and len(resp["Metrics"]) > 0:
            for metric in resp["Metrics"]:
                if metric["Namespace"] == self.namespace and metric["MetricName"] == self.metric_name:
                    if {'Value': self.asg_name, 'Name': 'AutoScalingGroupName'} in metric["Dimensions"]:
                        ASG_EC2S.append(metric)
                else:
                    continue
            return (ASG_EC2S)
        else:
            self.logger.warning("Err _get_ec2_from_asg: Metrics not found. Please check response obj")

    def _get_running_ec2(self,metric_list_with_asgec2):
        client = boto3.client("ec2",region_name=self.region_name)
        runningec2=[]
        extractedinstanceid=[]
        metric_list_with_asgec2=metric_list_with_asgec2

        if len(metric_list_with_asgec2)<1:
            return
        for item in metric_list_with_asgec2:
            if item["Dimensions"][0].get('Name') == "InstanceId":
                instanceid=item["Dimensions"][0].get('Value') #get the instanceid from instancelist [{'Namespace': 'CWAgent', 'MetricName': 'mem_used_percent', 'Dimensions': [{'Name': 'InstanceId', 'Value': 'i-0bbe91a73726127df'},
            else:
                continue
            extractedinstanceid.append(instanceid)
        for instid in extractedinstanceid:
            try:
                response = client.describe_instance_status(
                    InstanceIds=[instid],
                    IncludeAllInstances=False
                )
                for ec2 in response["InstanceStatuses"]:
                    runningec2.append(ec2.get("InstanceId"))
            except Exception as e:
                self.logger.warning("Exception in _get_running_ec2 :" + str(e))
                continue
        return(runningec2)

    def _get_memory_usage(self,ecm,dbhandler):
        start_time = datetime.utcnow() - timedelta(minutes=5)
        end_time = datetime.utcnow()
        period = 300
        cloudwatch = boto3.client('cloudwatch', region_name=self.region_name)
        res = cloudwatch.get_metric_statistics(
            Namespace=ecm['Namespace'],
            MetricName=ecm['MetricName'],
            Dimensions=ecm['Dimensions'],
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=['Average']
        )
        if len(res["Datapoints"])>0:
            memusage = res["Datapoints"][0]['Average']
            instance_id = ecm['Dimensions'][0]['Value']
            # get instance type to find memory
            ec2_client = boto3.client('ec2',region_name=self.region_name)
            response = ec2_client.describe_instances(InstanceIds=[instance_id])
            instance_type = response['Reservations'][0]['Instances'][0]['InstanceType']

            # get total memory in MB
            response = ec2_client.describe_instance_types(InstanceTypes=[instance_type])
            totalmemory = response['InstanceTypes'][0]['MemoryInfo']['SizeInMiB']

            # get pubip
            response = ec2_client.describe_instances(InstanceIds=[instance_id])
            public_ip = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
            data = {"instance_id":instance_id, "public_ip": public_ip, "memusage": memusage, "total_memory": totalmemory, "asg_name":self.asg_name, "region_name":self.region_name}
            dbhandler.insert_memusage_data(data)
        else:
            return False


def main():
    print("Use main")


if __name__ == "__main__":
    main()