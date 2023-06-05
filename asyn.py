import boto3
from datetime import datetime, timedelta
namespace="CWAgent"
metric_name="disk_used_percent"
asg_name="MoodleCloudASG"
region_name="us-west-2"
mountpath="/"
# cw_client_asg = boto3.client('autoscaling', 'us-west-2')
# response = cw_client_asg.describe_auto_scaling_groups(AutoScalingGroupNames=['MoodleCloudASG'])
# # return false if the asg name is not found
# if not response["AutoScalingGroups"]:
#     print("no response stuff")
ASG_EC2S = []
cloudwatch_client = boto3.client('cloudwatch', region_name="us-west-2")
resp = cloudwatch_client.list_metrics(
    Namespace="CWAgent",
    MetricName="disk_used_percent"
)
if "Metrics" in resp:
    for metric in resp["Metrics"]:
        if metric["Namespace"] == namespace and metric["MetricName"] == metric_name:
            if {'Value': asg_name, 'Name': 'AutoScalingGroupName'} in metric["Dimensions"] and {'Name': 'path', 'Value': mountpath} in metric["Dimensions"]:
                ASG_EC2S.append(metric)
        else:
            continue
    print(ASG_EC2S)
else:
   print("Err _get_ec2_from_asg: Metrics not found. Please check response obj")

#{'Name': 'path', 'Value': '/'}, {'Name': 'InstanceId', 'Value': 'i-03846106c36376830'},
# cloudwatch_client = boto3.client('cloudwatch')
#
# # Specify the region, instance ID, metric details, and ASG name
# region = 'us-west-2'
# instance_id = 'i-03846106c36376830'
# namespace = 'CWAgent'
# metric_name = 'disk_used_percent'
# asg_name = 'MoodleCloudASG'
#
# # Set the time range for the metric data
# end_time = datetime.utcnow()
# start_time = end_time - timedelta(minutes=5)
#
# # Retrieve the disk usage metric data
# response = cloudwatch_client.get_metric_data(
#     MetricDataQueries=[
#         {
#             'Id': 'disk_usage',
#             'MetricStat': {
#                 'Metric': {
#                     'Namespace': namespace,
#                     'MetricName': metric_name,
#                     'Dimensions':  [{'Name': 'path', 'Value': '/'}, {'Name': 'InstanceId', 'Value': 'i-03846106c36376830'}, {'Name': 'AutoScalingGroupName', 'Value': 'MoodleCloudASG'}]
#                 },
#                 'Period': 300,
#                 'Stat': 'Average'
#             },
#             'ReturnData': True
#         }
#     ],
#     StartTime=start_time,
#     EndTime=end_time
# )
#
# print('-------------------------\n\n')
# print(response)
