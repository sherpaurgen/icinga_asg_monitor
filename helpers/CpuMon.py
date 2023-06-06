#!/monitoringScripts/VENVT/bin/python
import os
import boto3
import logging
from datetime import datetime, timedelta
import concurrent.futures
from helpers.dbHandler import DbHandler


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
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", '%Y-%m-%d %H:%M:%S')
        file_handler = logging.FileHandler("/tmp/custom_ec2_info_fetcher.log")
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        return logger

    def _get_dns_ip(self,instance_id):
        cw_cli_ec2 = boto3.client('ec2', region_name=self.region_name)
        response = cw_cli_ec2.describe_instances(InstanceIds=[instance_id])
        instance_name = ''
        if len(response['Reservations']) < 1:
            return (False)
        try:
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    public_ip = instance.get('PublicIpAddress', 'NA')
                    dns_name = instance.get('PublicDnsName', 'NA')
                    private_ip = instance.get('PrivateIpAddress', 'NA')
                    state = instance['State']['Code']
                    # get asg name of instance
                    # {'Key': 'aws:autoscaling:groupName', 'Value': 'MoodleCloudASG'}
                    for tag in instance['Tags']:
                        if tag['Key'] == 'aws:autoscaling:groupName':
                            asg_name = tag.get('Value')
                    # Get the instance name if its set
                    for tag in instance['Tags']:
                        if tag['Key'] == 'Name':
                            instance_name = tag.get('Value', asg_name+"_"+instance_id)
                            if len(instance_name) < 1:
                                instance_name = asg_name+"_"+instance_id
                            break
                        else:
                            instance_name = asg_name+"_"+instance_id
                    return {"instance_id":instance_id,"public_ip":public_ip,"asg_name":asg_name,
                            "dns_name":dns_name,"private_ip":private_ip,"state":state,"instance_name":instance_name}
        except Exception as e:
            self.logger.warning("_get_dns_ip Exception:" + str(e))

    def _get_running_instances(self,running_instances):
        cw_client_asg = boto3.client('autoscaling', region_name=self.region_name)
        response = cw_client_asg.describe_auto_scaling_groups(AutoScalingGroupNames=[self.asg_name])
        # return false if the asg name is not found
        if not response["AutoScalingGroups"]:
            self.logger.warning("Nothing found inside Group "+self.asg_name+" in " +self.region_name)
        else:
            instancestmp = response['AutoScalingGroups'][0]['Instances']
            futures=[]
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                for instance in instancestmp:
                    instance_id = instance['InstanceId']
                    # get publicip, private ip of running instance
                    futures.append(executor.submit(self._get_dns_ip,instance_id))
                for completed_task in concurrent.futures.as_completed(futures):
                    try:
                        result=completed_task.result()
                        if result is None:
                            continue
                        else:
                            running_instances.append(
                            {"instance_id": result["instance_id"], "public_ip": result["public_ip"],
                             "private_ip": result["private_ip"], "dns_name": result["dns_name"],
                             "instance_name": result["instance_name"], "state": result["state"],
                             "region_name":self.region_name,"asg_name":result["asg_name"]})
                    except Exception as e:
                        self.logger.warning("_get_running_instances: Exception: "+str(e))
            return (running_instances)

    def _get_metric_statistics_of_instance_savetolist(self,instancerunning):
        try:
            script_home = os.path.dirname(os.path.abspath(__file__))
            dbfile = script_home + "/icinga.db"
            dbcon = DbHandler(dbfile)
            cw_cli = boto3.client('cloudwatch', region_name=instancerunning["region_name"])
            instance_id = instancerunning['instance_id']
            dimensions = [{'Name': 'InstanceId', 'Value': instance_id }]
            response = cw_cli.get_metric_statistics(
                Namespace="AWS/EC2",
                MetricName="CPUUtilization",
                Dimensions=dimensions,
                StartTime=datetime.utcnow() - timedelta(seconds=600),
                EndTime=datetime.utcnow(),
                Period=300,
                Statistics=['Average']
            )

            if len(response["Datapoints"]) == 0:
                print(f"Datapoint empty Region:"+instancerunning["region_name"]+instancerunning["instance_id"]+instancerunning["asg_name"])
                print(response)
                print("Make sure cloudwatch agent is installed or check the CW logs")

            if len(response["Datapoints"])>0:
                cpuusage = response["Datapoints"][0].get("Average", 0)
            else:
                return
            # Extract the public ip of running instance from response.
            try:
                public_ip = instancerunning["public_ip"]
            except Exception as e:
                public_ip = instancerunning["private_ip"]
                self.logger.warning("_get_metric_statistics_of_instance_savetodb : public ip not found, Using private ip for " + instance_id +str(e))

            data = { "instance_id": instance_id, "public_ip": public_ip, "private_ip": instancerunning["private_ip"],
                     "instance_name": instancerunning["instance_name"], "cpuusage": cpuusage,
                    "asgname": instancerunning["asg_name"], "region_name": self.region_name }
            return data

        except Exception as e:
            self.logger.warning("_get_metric_statistics_of_instance_savetodb: Exception: " + str(e))
            return

    def _get_cpu_utilization(self, running_instances):
        ft = []
        allcpudata=[]
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for instance in running_instances:
                ft.append(executor.submit(self._get_metric_statistics_of_instance_savetolist,instance))
            for future in concurrent.futures.as_completed(ft):
                allcpudata.append(future.result())
        return allcpudata

def main():
    print("Use main.py")


if __name__ == "__main__":
    main()

