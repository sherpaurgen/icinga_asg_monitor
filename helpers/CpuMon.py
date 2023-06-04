#!/monitoringScripts/VENVT/bin/python
import boto3
import logging
from datetime import datetime, timedelta
import concurrent.futures
import time
import json




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
                    # Get the instance name if its set
                    for tag in instance['Tags']:
                        if tag['Key'] == 'Name':
                            instance_name = tag.get('Value', self.asg_name+"_"+instance_id)
                            if len(instance_name) < 1:
                                instance_name = self.asg_name+"_"+instance_id
                            break
                        else:
                            instance_name = self.asg_name+"_"+instance_id
                    return {"instance_id":instance_id,"public_ip":public_ip,"dns_name":dns_name,"private_ip":private_ip,"state":state,"instance_name":instance_name}
        except Exception as e:
            self.logger.warning("_get_dns_ip Exception:" + str(e))

    def _get_running_instances(self):
        tstart = time.perf_counter()
        cw_client_asg = boto3.client('autoscaling', region_name=self.region_name)
        response = cw_client_asg.describe_auto_scaling_groups(AutoScalingGroupNames=[self.asg_name])
        tend = time.perf_counter()
        print(f"describe_auto_scaling_groups spent {(tend-tstart):.3f} seconds ")
        # return false if the asg name is not found
        if not response["AutoScalingGroups"]:
            return (False)
        else:
            instancestmp = response['AutoScalingGroups'][0]['Instances']
            running_instances = []
            futures=[]
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                for instance in instancestmp:
                    instance_id = instance['InstanceId']
                    # get publicip,privateip of running instance
                    futures.append(executor.submit(self._get_dns_ip,instance_id))
                    result=self._get_dns_ip(instance_id)
                for completed_task in concurrent.futures.as_completed(futures):
                    try:
                        result=completed_task.result()
                        running_instances.append(
                            {"instance_id": result["instance_id"], "public_ip": result["public_ip"],
                             "private_ip": result["private_ip"], "dns_name": result["dns_name"],
                             "instance_name": result["instance_name"], "state": result["state"]})
                    except Exception as e:
                        self.logger.warning("_get_running_instances: Exception: "+str(e))
            return (running_instances)

    def _get_metric_statistics_of_instance_savetodb(self,instancerunning,db_handler):
        tstart = time.perf_counter()
        try:
            instance_id = instancerunning['instance_id']
            cw_cli = boto3.client('cloudwatch', region_name=self.region_name)
            dimensions = [{'Name': 'InstanceId', 'Value': instance_id }]
            response = cw_cli.get_metric_statistics(
                Namespace=self.namespace,
                MetricName=self.metric_name,
                Dimensions=dimensions,
                StartTime=datetime.utcnow() - timedelta(seconds=600),
                EndTime=datetime.utcnow(),
                Period=300,
                Statistics=['Average']
            )
            cpuusage = response["Datapoints"][0].get("Average", 0)
            tstop = time.perf_counter()
            timeelapsed=(tstop-tstart)
            print(f"{timeelapsed:.3f} second timeelapsed for getMetric statistics: {instance_id}")
            #extract the public ip of running instance from response
            try:
                public_ip = instancerunning["public_ip"]
            except Exception as e:
                public_ip=instancerunning["private_ip"]
                self.logger.warning("_get_metric_statistics_of_instance_savetodb : public ip not found, Using private ip for "+instance_id +str(e))
            data = {"instance_id": instance_id, "public_ip": public_ip,"private_ip":instancerunning["private_ip"],"instance_name":instancerunning["instance_name"], "cpuusage": cpuusage,
                    "asgname": self.asg_name, "region_name": self.region_name}
            db_handler.insert_cpuusage_data(data)
        except Exception as e:
            self.logger.warning("_get_metric_statistics_of_instance_savetodb: Exception: "+ str(e))

    def _get_cpu_utilization(self, running_instances, db_handler):
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures=[]
            for instance in running_instances:
                futures.append(executor.submit(self._get_metric_statistics_of_instance_savetodb,instance,db_handler))
            for future in concurrent.futures.as_completed(futures):
                try:
                    pass
                except Exception as e:
                    print("_get_cpu_utilization Exception:"+str(e))


def main():
    print("Use main.py")


if __name__ == "__main__":
    main()

