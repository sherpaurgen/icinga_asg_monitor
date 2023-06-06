import boto3


ec2_client = boto3.client('ec2',region_name='us-west-2')


instance_id = 'i-03846106c36376830'


response = ec2_client.describe_instances(InstanceIds=[instance_id])
print(response)


