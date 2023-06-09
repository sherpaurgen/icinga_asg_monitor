
import boto3

mount_point_list=["/","/datadrive"]
asg_name_list = ["Demoasg","northernAsg"]


def get_metriclist_from_asg(instance_id,region_name,namespace,metric_name,asg_name_list,mount_point_list):

    instancemetric=[]
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
        for asg_name in asg_name_list:
            for mountpath in mount_point_list:
                for metric in resp["Metrics"]:
                    if metric["Namespace"] == namespace and metric["MetricName"] == metric_name:

                        if {'Name': 'AutoScalingGroupName','Value': asg_name } in metric["Dimensions"] and {'Name': 'path', 'Value': mountpath} in metric["Dimensions"]:
                            instancemetric.append(metric)

    else:
        print("no resp")
    print({"instance_id":instance_id,"metric":instancemetric })
    return {"instance_id":instance_id,"metric":instancemetric }

get_metriclist_from_asg('i-0c10cfcc8a0bec161','us-east-1','CWAgent','disk_used_percent',asg_name_list, mount_point_list)