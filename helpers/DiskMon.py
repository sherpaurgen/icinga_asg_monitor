#!/monitoringScripts/VENVT/bin/python
import boto3
import logging
from datetime import datetime, timedelta

def get_disk_used_percent(instance_id,region_name,asg_name,metric_name,namespace,DimensionsData):
    result=[]
    if len(DimensionsData) == 0: # instance which dont have CWAgent installed will have this False
        logging.warning(f"instance_id : missing CWAgent")
        return False
    else:
        try:
            instance_id = instance_id
            region_name = region_name
            asg_name = asg_name
            for instMetricData in DimensionsData:
                dim = instMetricData['Dimensions']
                mntpoint = instMetricData['Dimensions'][0]['Value']  # extract the mountpoint
                # print(f"mountpoint is { mntpoint} \n {dim} \n---\n")
                cloudwatch_client = boto3.client('cloudwatch', region_name=region_name)
                end_time = datetime.utcnow()
                start_time = end_time - timedelta(minutes=5)
                response = cloudwatch_client.get_metric_data(
                    MetricDataQueries=[
                        {
                            'Id': 'disk_utilization',
                            'MetricStat': {
                                'Metric': {
                                    'Namespace': namespace,
                                    'MetricName': metric_name,
                                    'Dimensions': dim
                                },
                                'Period': 60,
                                'Stat': 'Average',
                            }
                        },
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                )
                if len(response['MetricDataResults'][0]['Values']) > 0:
                    data_points = response['MetricDataResults'][0]['Values']
                    disk_usage_percent = data_points[-1]
                else:
                    disk_usage_percent = -1

                result.append({'instance_id': instance_id, 'region_name': region_name, 'asg_name': asg_name,
                            'disk_used': disk_usage_percent,'mount_point': mntpoint})
        except Exception as e:
           logging.warning("get_disk_used_percent Exception: " + str(e))
    return result
#(item['instance_id'],item['region_name'],sto_namespace,sto_metric_name,asg_list, mount_point_list)
def get_metriclist_for_instance(instance_id,region_name,namespace,metric_name,asg_name,mount_point_list):
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
            for mountpath in mount_point_list:
                for metric in resp["Metrics"]:
                    if metric["Namespace"] == namespace and metric["MetricName"] == metric_name:
                        if {'Name': 'AutoScalingGroupName', 'Value': asg_name} in metric["Dimensions"] and {'Name': 'path',
                                                                                                            'Value': mountpath} in \
                                metric["Dimensions"]:
                            instancemetric.append(metric)
    else:
        logging.warning("empty response")
    #item['instance_id'],item['region_name'],item['asg_name'],sto_metric_name,sto_namespace,mount_point_list)
    return {"instance_id":instance_id,"region_name":region_name,"asg_name":asg_name,
            "metric_name": metric_name,"namespace":namespace,"DimensionsData":instancemetric }





