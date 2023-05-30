### DiskMon.py > _get_ec2_from_asg

Sample response 
```json
{'Metrics': [{'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/'}, {'Name': 'InstanceId', 'Value': 'i-08e12a7cdbd1bb974'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'xvda1'}, {'Name': 'fstype', 'Value': 'ext4'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'InstanceId', 'Value': 'i-08e12a7cdbd1bb974'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/dev'}, {'Name': 'InstanceId', 'Value': 'i-08e12a7cdbd1bb974'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'devtmpfs'}, {'Name': 'fstype', 'Value': 'devtmpfs'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/dev/shm'}, {'Name': 'InstanceId', 'Value': 'i-08e12a7cdbd1bb974'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'tmpfs'}, {'Name': 'fstype', 'Value': 'tmpfs'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/run'}, {'Name': 'InstanceId', 'Value': 'i-08e12a7cdbd1bb974'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'tmpfs'}, {'Name': 'fstype', 'Value': 'tmpfs'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/run/lock'}, {'Name': 'InstanceId', 'Value': 'i-08e12a7cdbd1bb974'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'tmpfs'}, {'Name': 'fstype', 'Value': 'tmpfs'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/snap/amazon-ssm-agent/6312'}, {'Name': 'InstanceId', 'Value': 'i-08e12a7cdbd1bb974'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'loop0'}, {'Name': 'fstype', 'Value': 'squashfs'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/mydata'}, {'Name': 'InstanceId', 'Value': 'i-08e12a7cdbd1bb974'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'xvdf'}, {'Name': 'fstype', 'Value': 'ext4'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/snap/core18/2745'}, {'Name': 'InstanceId', 'Value': 'i-08e12a7cdbd1bb974'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'loop1'}, {'Name': 'fstype', 'Value': 'squashfs'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/snap/core20/1879'}, {'Name': 'InstanceId', 'Value': 'i-08e12a7cdbd1bb974'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'loop2'}, {'Name': 'fstype', 'Value': 'squashfs'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/snap/lxd/24322'}, {'Name': 'InstanceId', 'Value': 'i-08e12a7cdbd1bb974'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'loop3'}, {'Name': 'fstype', 'Value': 'squashfs'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/snap/snapd/19122'}, {'Name': 'InstanceId', 'Value': 'i-08e12a7cdbd1bb974'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'loop4'}, {'Name': 'fstype', 'Value': 'squashfs'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/boot/efi'}, {'Name': 'InstanceId', 'Value': 'i-08e12a7cdbd1bb974'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'xvda15'}, {'Name': 'fstype', 'Value': 'vfat'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/run/snapd/ns'}, {'Name': 'InstanceId', 'Value': 'i-08e12a7cdbd1bb974'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'tmpfs'}, {'Name': 'fstype', 'Value': 'tmpfs'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/snap/core20/1891'}, {'Name': 'InstanceId', 'Value': 'i-08e12a7cdbd1bb974'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'loop5'}, {'Name': 'fstype', 'Value': 'squashfs'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/run/user/1000'}, {'Name': 'InstanceId', 'Value': 'i-08e12a7cdbd1bb974'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'tmpfs'}, {'Name': 'fstype', 'Value': 'tmpfs'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/'}, {'Name': 'InstanceId', 'Value': 'i-0bbe91a73726127df'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'xvda1'}, {'Name': 'fstype', 'Value': 'ext4'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'InstanceId', 'Value': 'i-0bbe91a73726127df'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/dev'}, {'Name': 'InstanceId', 'Value': 'i-0bbe91a73726127df'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'devtmpfs'}, {'Name': 'fstype', 'Value': 'devtmpfs'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/dev/shm'}, {'Name': 'InstanceId', 'Value': 'i-0bbe91a73726127df'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'tmpfs'}, {'Name': 'fstype', 'Value': 'tmpfs'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/run'}, {'Name': 'InstanceId', 'Value': 'i-0bbe91a73726127df'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'tmpfs'}, {'Name': 'fstype', 'Value': 'tmpfs'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/run/lock'}, {'Name': 'InstanceId', 'Value': 'i-0bbe91a73726127df'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'tmpfs'}, {'Name': 'fstype', 'Value': 'tmpfs'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/snap/amazon-ssm-agent/6312'}, {'Name': 'InstanceId', 'Value': 'i-0bbe91a73726127df'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'loop0'}, {'Name': 'fstype', 'Value': 'squashfs'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/snap/core18/2745'}, {'Name': 'InstanceId', 'Value': 'i-0bbe91a73726127df'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'loop1'}, {'Name': 'fstype', 'Value': 'squashfs'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/snap/core20/1879'}, {'Name': 'InstanceId', 'Value': 'i-0bbe91a73726127df'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'loop2'}, {'Name': 'fstype', 'Value': 'squashfs'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/snap/lxd/24322'}, {'Name': 'InstanceId', 'Value': 'i-0bbe91a73726127df'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'loop3'}, {'Name': 'fstype', 'Value': 'squashfs'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/snap/snapd/19122'}, {'Name': 'InstanceId', 'Value': 'i-0bbe91a73726127df'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'loop4'}, {'Name': 'fstype', 'Value': 'squashfs'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/boot/efi'}, {'Name': 'InstanceId', 'Value': 'i-0bbe91a73726127df'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'xvda15'}, {'Name': 'fstype', 'Value': 'vfat'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/run/snapd/ns'}, {'Name': 'InstanceId', 'Value': 'i-0bbe91a73726127df'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'tmpfs'}, {'Name': 'fstype', 'Value': 'tmpfs'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/snap/core20/1891'}, {'Name': 'InstanceId', 'Value': 'i-0bbe91a73726127df'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'loop5'}, {'Name': 'fstype', 'Value': 'squashfs'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/mydata'}, {'Name': 'InstanceId', 'Value': 'i-0bbe91a73726127df'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'xvdf'}, {'Name': 'fstype', 'Value': 'ext4'}]}, {'Namespace': 'CWAgent', 'MetricName': 'disk_used_percent', 'Dimensions': [{'Name': 'path', 'Value': '/run/user/1000'}, {'Name': 'InstanceId', 'Value': 'i-0bbe91a73726127df'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}, {'Name': 'device', 'Value': 'tmpfs'}, {'Name': 'fstype', 'Value': 'tmpfs'}]}], 'ResponseMetadata': {'RequestId': '38be60b2-b136-4ad7-b4bc-bfbf34545727', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '38be60b2-b136-4ad7-b4bc-bfbf34545727', 'content-type': 'text/xml', 'content-length': '29574', 'date': 'Sun, 28 May 2023 17:53:40 GMT'}, 'RetryAttempts': 0}}
```
check the cloudwatch config
```json
Check saved config file to /opt/aws/amazon-cloudwatch-agent/bin/config.json successfully.
Current config as follows:
{
	"agent": {
		"metrics_collection_interval": 60,
		"run_as_user": "root"
	},
	"metrics": {
		"aggregation_dimensions": [
			[
				"InstanceId"
			]
		],
		"append_dimensions": {
			"AutoScalingGroupName": "${aws:AutoScalingGroupName}",
			"ImageId": "${aws:ImageId}",
			"InstanceId": "${aws:InstanceId}",
			"InstanceType": "${aws:InstanceType}"
		},
		"metrics_collected": {
			"cpu": {
				"measurement": [
					"cpu_usage_idle",
					"cpu_usage_iowait",
					"cpu_usage_user",
					"cpu_usage_system"
				],
				"metrics_collection_interval": 60,
				"resources": [
					"*"
				],
				"totalcpu": false
			},
			"disk": {
				"measurement": [
					"used_percent",
					"inodes_free"
				],
				"metrics_collection_interval": 60,
				"resources": [
					"*"
				]
			},
			"diskio": {
				"measurement": [
					"io_time"
				],
				"metrics_collection_interval": 60,
				"resources": [
					"*"
				]
			},
			"mem": {
				"measurement": [
					"mem_used_percent"
				],
				"metrics_collection_interval": 60
			},
			"swap": {
				"measurement": [
					"swap_used_percent"
				],
				"metrics_collection_interval": 60
			}
		}
	}
}

```

---resp START-----_get_ec2_from_asg
```json
{
	'Metrics': [{
		'Namespace': 'CWAgent',
		'MetricName': 'mem_used_percent',
		'Dimensions': [{
			'Name': 'InstanceId',
			'Value': 'i-0bbe91a73726127df'
		}, {
			'Name': 'AutoScalingGroupName',
			'Value': 'AsgUsh'
		}, {
			'Name': 'ImageId',
			'Value': 'ami-03f65b8614a860c29'
		}, {
			'Name': 'InstanceType',
			'Value': 't2.micro'
		}]
	}, {
		'Namespace': 'CWAgent',
		'MetricName': 'mem_used_percent',
		'Dimensions': [{
			'Name': 'InstanceId',
			'Value': 'i-0bbe91a73726127df'
		}]
	}, {
		'Namespace': 'CWAgent',
		'MetricName': 'mem_used_percent',
		'Dimensions': [{
			'Name': 'InstanceId',
			'Value': 'i-058421acf90b9c505'
		}]
	}, {
		'Namespace': 'CWAgent',
		'MetricName': 'mem_used_percent',
		'Dimensions': [{
			'Name': 'InstanceId',
			'Value': 'i-058421acf90b9c505'
		}, {
			'Name': 'AutoScalingGroupName',
			'Value': 'AsgUsh'
		}, {
			'Name': 'ImageId',
			'Value': 'ami-03f65b8614a860c29'
		}, {
			'Name': 'InstanceType',
			'Value': 't2.micro'
		}]
	}, {
		'Namespace': 'CWAgent',
		'MetricName': 'mem_used_percent',
		'Dimensions': [{
			'Name': 'InstanceId',
			'Value': 'i-08e12a7cdbd1bb974'
		}, {
			'Name': 'AutoScalingGroupName',
			'Value': 'AsgUsh'
		}, {
			'Name': 'ImageId',
			'Value': 'ami-03f65b8614a860c29'
		}, {
			'Name': 'InstanceType',
			'Value': 't2.micro'
		}]
	}, {
		'Namespace': 'CWAgent',
		'MetricName': 'mem_used_percent',
		'Dimensions': [{
			'Name': 'InstanceId',
			'Value': 'i-08e12a7cdbd1bb974'
		}]
	}],
	'ResponseMetadata': {
		'RequestId': 'f72968aa-613f-4a34-be2f-f110cca284bc',
		'HTTPStatusCode': 200,
		'HTTPHeaders': {
			'x-amzn-requestid': 'f72968aa-613f-4a34-be2f-f110cca284bc',
			'content-type': 'text/xml',
			'content-length': '3051',
			'date': 'Tue, 30 May 2023 03:45:07 GMT'
		},
		'RetryAttempts': 0
	}
}
```
Value of ASG_EC2S = []
```json
[{'Namespace': 'CWAgent', 'MetricName': 'mem_used_percent', '
Dimensions': [{'Name': 'InstanceId', 'Value': 'i-0bbe91a73726127df'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}]
}, {'Namespace': 'CWAgent', 'MetricName': 'mem_used_percent', '
Dimensions': [{'Name': 'InstanceId', 'Value': 'i-058421acf90b9c505'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}]
}, {'Namespace': 'CWAgent', 'MetricName': 'mem_used_percent', '
Dimensions': [{'Name': 'InstanceId', 'Value': 'i-08e12a7cdbd1bb974'}, {'Name': 'AutoScalingGroupName', 'Value': 'AsgUsh'}, {'Name': 'ImageId', 'Value': 'ami-03f65b8614a860c29'}, {'Name': 'InstanceType', 'Value': 't2.micro'}]
}]
```

response from describe_instance_status (gives running ec2 list)
```json
{'InstanceStatuses': [
        {'AvailabilityZone': 'us-west-2a', 'InstanceId': 'i-058421acf90b9c505', 'InstanceState': {'Code': 16, 'Name': 'running'
            }, 'InstanceStatus': {'Details': [
                    {'Name': 'reachability', 'Status': 'passed'
                    }
                ], 'Status': 'ok'
            }, 'SystemStatus': {'Details': [
                    {'Name': 'reachability', 'Status': 'passed'
                    }
                ], 'Status': 'ok'
            }
        },
        {'AvailabilityZone': 'us-west-2a', 'InstanceId': 'i-0bbe91a73726127df', 'InstanceState': {'Code': 16, 'Name': 'running'
            }, 'InstanceStatus': {'Details': [
                    {'Name': 'reachability', 'Status': 'passed'
                    }
                ], 'Status': 'ok'
            }, 'SystemStatus': {'Details': [
                    {'Name': 'reachability', 'Status': 'passed'
                    }
                ], 'Status': 'ok'
            }
        }
    ], 'ResponseMetadata': {'RequestId': '4fb0b246-7e61-4249-bc8d-a6260b60f161', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '4fb0b246-7e61-4249-bc8d-a6260b60f161', 'cache-control': 'no-cache, no-store', 'strict-transport-security': 'max-age=31536000; includeSubDomains', 'content-type': 'text/xml;charset=UTF-8', 'content-length': '2011', 'date': 'Tue,
            30 May 2023 05: 19: 04 GMT', 'server': 'AmazonEC2'
        }, 'RetryAttempts': 0
    }
}
```

