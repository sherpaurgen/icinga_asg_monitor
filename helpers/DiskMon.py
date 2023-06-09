#!/monitoringScripts/VENVT/bin/python
import boto3
import logging
from datetime import datetime, timedelta



def create_logger(self):
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



def get_disk_used_percent(instance_id,region_name,asg_name,Namespace,MetricName,mount_point):
    try:
        start_time = datetime.utcnow() - timedelta(minutes=5)
        end_time = datetime.utcnow()
        period = 300
        cloudwatch = boto3.client('cloudwatch', region_name=region_name)

        Dimensions = [{'Name': 'InstanceId', 'Value': instance_id}]
        res = cloudwatch.get_metric_statistics(
            Namespace=Namespace,
            MetricName=MetricName,
            Dimensions=Dimensions,
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=['Average']
        )
        instance_id = instance_id
        mount_point = mount_point
        print("the response")
        print(res)
        print()
        # getting id and mount point
        for item in Dimensions:
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
                "asg_name": asg_name, "region_name": region_name}
        print(data)


    except Exception as e:
        logging.warning("_get_disk_used_percent Failed: " + str(e))


def get_metriclist_for_instance(instance_id,region_name,namespace,metric_name,asg_list,mount_point_list):
    instancemetric = []
    cloudwatch_client = boto3.client('cloudwatch', region_name=region_name)
    resp = cloudwatch_client.list_metrics(
        Namespace='CWAgent',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instance_id
            }
        ]
    )
    if "Metrics" in resp:
        for asg_name in asg_list:
            for mountpath in mount_point_list:
                for metric in resp["Metrics"]:
                    if metric["Namespace"] == namespace and metric["MetricName"] == metric_name:
                        if {'Name': 'AutoScalingGroupName', 'Value': asg_name} in metric["Dimensions"] and {'Name': 'path',
                                                                                                            'Value': mountpath} in \
                                metric["Dimensions"]:
                            instancemetric.append(metric)
    else:
        logging.warning("empty response")
    return {"instance_id":instance_id,"Dimensions":instancemetric }





