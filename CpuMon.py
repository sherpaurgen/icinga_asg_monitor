import boto3
import logging
from jinja2 import Template
from datetime import datetime, timedelta
import subprocess
import yaml
import os

import sqlite3
from dbHandler import DbHandler

class AsgCPUMonitor:
    def __init__(self, asg_name, region_name, namespace, metric_name):
        self.asg_name = asg_name
        self.region_name = region_name
        self.namespace = namespace
        self.metric_name = metric_name
        self.logger = self._create_logger()

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

    def _get_running_instances(self):
        cw_client_asg = boto3.client('autoscaling',region_name=self.region_name)
        response = cw_client_asg.describe_auto_scaling_groups(AutoScalingGroupNames=[self.asg_name])
        instancestmp = response['AutoScalingGroups'][0]['Instances']
        print(instancestmp)
        cw_cli_ec2 = boto3.client('ec2', region_name=self.region_name)
        running_instances=[]
        for instance in instancestmp:
            instance_id = instance['InstanceId']
            response = cw_cli_ec2.describe_instances(InstanceIds=[instance_id])
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
                    running_instances.append(
                        {"instance_id": instance_id, "pub_ip": public_ip, "dns_name": dns_name,
                         "instance_name": instance_name,
                         "state": state})
            except Exception as e:
                self.logger.warning("_get_ec2_detail Error:" + str(e))
        return(running_instances)

    def _get_cpu_utilization(self,running_instances,db_handler):
        cw_cli = boto3.client('cloudwatch',region_name=self.region_name)
        for instance in running_instances:
            dimensions = [{'Name': 'InstanceId', 'Value': instance["instance_id"]}]
            response = cw_cli.get_metric_statistics(
                Namespace=self.namespace,
                MetricName=self.metric_name,
                Dimensions=dimensions,
                StartTime=datetime.utcnow() - timedelta(seconds=600),
                EndTime=datetime.utcnow(),
                Period=300,
                Statistics=['Average']
            )
            print("The Rres:")
            cpuusage=response["Datapoints"][0].get("Average",0)
            data = {"instance_id": instance["instance_id"], "cpuusage": cpuusage, "asgname": self.asg_name}

            db_handler.insert_cpuusage_data(data)

def main():
    obj=AsgCPUMonitor("AsgUsh", "us-west-2", "AWS/EC2", "CPUUtilization")
    script_home = os.path.dirname(os.path.abspath(__file__))
    dbfile = script_home + "/monitoring.db"
    db_handler = DbHandler(dbfile)
    runninginstances = obj._get_running_instances()
    obj._get_cpu_utilization(runninginstances,db_handler)
    db_handler.close_connection()
if __name__ == "__main__":
        main()

