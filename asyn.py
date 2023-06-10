import boto3
from datetime import datetime
from datetime import timedelta

totalec2=[
[{'Namespace': 'CWAgent', 'Dimensions': [{'Name': 'path', 'Value': '/'}, {'Name': 'InstanceId', 'Value': 'i-0c10cfcc8a0bec161'}, {'Name': 'AutoScalingGroupName', 'Value': 'northernAsg'}, {'Name': 'ImageId', 'Value': 'ami-053b0d53c279acc90'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'xvda1'}, {'Name': 'fstype', 'Value': 'ext4'}]},{'Namespace': 'CWAgent', 'Dimensions': [{'Name': 'path', 'Value': '/datadrive'}, {'Name': 'InstanceId', 'Value': 'i-0c10cfcc8a0bec161'}, {'Name': 'AutoScalingGroupName', 'Value': 'northernAsg'}, {'Name': 'ImageId', 'Value': 'ami-053b0d53c279acc90'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'xvdb'}, {'Name': 'fstype', 'Value': 'ext4'}]}]]

def get_disk_used_percent(instance_id, region_name, asg_name, metric_name, namespace, DimensionsData, disk_data):
    print(DimensionsData)
    print("\n\n")
    count = 0
    result = []
    if len(DimensionsData) < 1:
        print("less Dimensiondata")
    else:
        for instMetricData in DimensionsData:
            count = count + 1
            dim = instMetricData['Dimensions']
            mntpoint = instMetricData['Dimensions'][0]['Value']  # extract the mountpoint
            print(f"mountpoint is {mntpoint} \n---\n")
            print(f"The dimen {dim} \n\n")
            print(f"\nCount : {count}\n")
            try:
                print(f"call for {mntpoint}-boto done----------------")
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
                print(f"\ndim used: {dim}\n")
                print(f"{response}\n\n")
            except Exception as e:
                print(e)
            if len(response['MetricDataResults'][0]['Values']) > 0:
                data_points = response['MetricDataResults'][0]['Values']
                disk_usage_percent = data_points[-1]
            else:
                disk_usage_percent = -1

            result.append({'instance_id': instance_id, 'region_name': region_name, 'asg_name': asg_name,
                        'disk_used': disk_usage_percent,'mount_point': mntpoint})

    return result
print("The final......\n\n")
print(get_disk_used_percent("i-0c10cfcc8a0bec161","us-east-1","northernAsg","CWAgent","disk_used_percent",totalec2[0],"asdf"))
