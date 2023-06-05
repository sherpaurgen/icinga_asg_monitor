#!/monitoringScripts/VENVT/bin/python
import boto3
import logging
from datetime import datetime, timedelta
import subprocess
import sqlite3


class AsgDiskMonitor:
    def __init__(self, asg_name, region_name, mountpath, namespace, metric_name, hosttemplatepath, icingahostfilepath):
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
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", '%Y-%m-%d %H:%M:%S')
        file_handler = logging.FileHandler("/tmp/custom_ec2_info_fetcher.log")
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        return logger

    def _get_metriclist_from_asg(self):
        cloudwatch_client = boto3.client('cloudwatch', region_name=self.region_name)
        resp = cloudwatch_client.list_metrics(
            Namespace=self.namespace,
            MetricName=self.metric_name
        )
        print(resp)
        # if "Metrics" in resp:
        #     self.logger.warning("Metrics found in the GET request")
        #     for metric in resp["Metrics"]:
        #         if metric["Namespace"] == self.namespace and metric["MetricName"] == self.metric_name:
        #             if {'Value': self.asg_name, 'Name': 'AutoScalingGroupName'} in metric["Dimensions"] and {'Name': 'path', 'Value': self.mountpath} in metric["Dimensions"]:
        #                 ASG_metriclist_for_mountPoint.append(metric)
        #         else:
        #             continue
        #     #returns the metric list
        #     print("ASG_metriclist_for_mountPoint--------")
        #     print(ASG_metriclist_for_mountPoint)
        #     print()
        #     return (ASG_metriclist_for_mountPoint)
        # else:
        #     self.logger.warning("Err: _get_metriclist_from_asg: Metrics not found. Please check response obj")

    def _get_disk_used_percent(self, ec2_ASG_metriclist, db_handler):
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
            mount_point = ""
            # getting id and mount point
            for item in ec2metric['Dimensions']:
                if item.get('Name') == 'InstanceId':
                    instance_id = item.get('Value')
                if item.get('Name') == 'path':
                    mount_point = item.get('Value')
            disk_usage = 0
            # getting disk usage from the response obj
            for point in res['Datapoints']:
                if 'Average' in point:
                    disk_usage = point['Average']
                    break
            data = {"instance_id": instance_id, "DiskUsage": disk_usage, "MountPoint": mount_point,
                    "asg_name": self.asg_name, "region_name": self.region_name}

            db_handler.insert_diskusage_data(data)
        except Exception as e:
            self.logger.warning("_get_disk_used_percent Failed: " + str(e))

    def _get_ec2_detail(self, instance_id):
        ec2_client = boto3.client('ec2', self.region_name)
        instance_id = instance_id
        try:
            response = ec2_client.describe_instances(InstanceIds=[instance_id])

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
                            instance_name = tag.get('Value', instance_id)
                            if len(instance_name) < 1:
                                instance_name = instance_id
                            break
                        else:
                            instance_name = instance_id
                return (
                    {"instance_id": instance_id, "pub_ip": public_ip, "dns_name": dns_name,
                     "instance_name": instance_name,
                     "state": state})
        except Exception as e:
            self.logger.warning("_get_ec2_detail Error:" + str(e))



    def verify_asg(self):
        cw_client_asg = boto3.client('autoscaling', region_name=self.region_name)
        response = cw_client_asg.describe_auto_scaling_groups(AutoScalingGroupNames=[self.asg_name])
        # return false if the asg name is not found
        if not response["AutoScalingGroups"]:
            return (False)
        else:
            return (True)



def main():
    print("Use main.py")

if __name__ == "__main__":
    main()