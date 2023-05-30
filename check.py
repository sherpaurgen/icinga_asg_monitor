import boto3

# Create a Boto3 EC2 client
ec2_client = boto3.client('ec2')

# Specify the instance ID
instance_id = 'i-058421acf90b9c505'


response = ec2_client.describe_instances(InstanceIds=[instance_id])
instance_type = response['Reservations'][0]['Instances'][0]['InstanceType']

# Retrieve the memory estimation based on the instance type
response = ec2_client.describe_instance_types(InstanceTypes=[instance_type])
memory = response['InstanceTypes'][0]['MemoryInfo']['SizeInMiB']

# Print the total memory of the instance
print("Total memory (RAM) of the instance:", memory, "MiB")