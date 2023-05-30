import boto3
import logging
from jinja2 import Template
from datetime import datetime, timedelta
import subprocess
import yaml
import os
from dbHandler import DbHandler

class AsgMemoryMonitor:
    def __init__(self, asg_name, region_name,namespace ,metric_name, hosttemplatepath, icingahostfilepath):
        self.asg_name = asg_name
        self.region_name = region_name
        self.namespace = namespace
        self.metric_name = metric_name
        self.logger = self._create_logger()
        self.hosttemplatepath = hosttemplatepath
        self.icingahostfilepath = icingahostfilepath


    def _create_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s",'%Y-%m-%d %H:%M:%S')
        file_handler = logging.FileHandler("/tmp/custom_ec2_info_fetcher.log")
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        return logger

    def verify_asg(self):
        cw_client_asg = boto3.client('autoscaling', region_name=self.region_name)
        response = cw_client_asg.describe_auto_scaling_groups(AutoScalingGroupNames=[self.asg_name])
        # return false if the asg name is not found
        if not response["AutoScalingGroups"]:
            self.logger("Error in verify_asg: ASG not found please check asg name exist in monitor_memory.yaml")
            return (False)
        else:
            return (True)

    def _get_metric_instanceid_from_asg(self):

        ASG_EC2S = []
        cloudwatch_client = boto3.client('cloudwatch', region_name=self.region_name)
        resp = cloudwatch_client.list_metrics(
            Namespace=self.namespace,
            MetricName=self.metric_name
        )
        # response has list of metrics + asg name and instance id
        if "Metrics" in resp and len(resp["Metrics"]) > 0:
            for metric in resp["Metrics"]:
                if metric["Namespace"] == self.namespace and metric["MetricName"] == self.metric_name:
                    if {'Value': self.asg_name, 'Name': 'AutoScalingGroupName'} in metric["Dimensions"]:
                        ASG_EC2S.append(metric)
                else:
                    continue
            return (ASG_EC2S)
        else:
            self.logger.warning("Err _get_ec2_from_asg: Metrics not found. Please check response obj")

    def _get_running_ec2(self,metric_list_with_asgec2):
        client = boto3.client("ec2",region_name=self.region_name)
        runningec2=[]
        extractedinstanceid=[]
        metric_list_with_asgec2=metric_list_with_asgec2
        for item in metric_list_with_asgec2:
            instanceid=item["Dimensions"][0].get('Value') #get the instanceid from instancelist [{'Namespace': 'CWAgent', 'MetricName': 'mem_used_percent', 'Dimensions': [{'Name': 'InstanceId', 'Value': 'i-0bbe91a73726127df'},
            extractedinstanceid.append(instanceid)
        try:
            response = client.describe_instance_status(
                InstanceIds=extractedinstanceid,
                IncludeAllInstances=False
            )
            for ec2 in response["InstanceStatuses"]:
                runningec2.append(ec2.get("InstanceId"))
        except Exception as e:
            self.logger("Exception in _get_running_ec2 :" + str(e))
        return(runningec2)

    def _get_memory_usage(self,ecm):
        start_time = datetime.utcnow() - timedelta(minutes=5)
        end_time = datetime.utcnow()
        period = 300
        cloudwatch = boto3.client('cloudwatch', region_name=self.region_name)
        res = cloudwatch.get_metric_statistics(
            Namespace=ecm['Namespace'],
            MetricName=ecm['MetricName'],
            Dimensions=ecm['Dimensions'],
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=['Average']
        )
        if len(res["Datapoints"])>0:
            memusageavgpct=res["Datapoints"][0]['Average']



def startProcessing(ASG_NAME, region_name, Namespace,
                          MetricName,hosttemplatepath,
                          icingahostfilepath,db_handler):
    adm1 = AsgMemoryMonitor(asg_name=ASG_NAME, region_name=region_name, namespace=Namespace,
                          metric_name=MetricName, hosttemplatepath=hosttemplatepath,
                          icingahostfilepath=icingahostfilepath)
    if adm1.verify_asg() is False:
        return
    metric_list_with_asgec2=adm1._get_metric_instanceid_from_asg()
    runningec2=adm1._get_running_ec2(metric_list_with_asgec2)
    # preparing list for ec2 that are powered on/running
    running_ec2_metric_list=[]
    for id in runningec2:
        for dim in metric_list_with_asgec2:
            if dim["Dimensions"][0]["Value"] == id:
                running_ec2_metric_list.append(dim)

    for ecm in running_ec2_metric_list:
        adm1._get_memory_usage(ecm)





def main():
    script_home = os.path.dirname(os.path.abspath(__file__))
    memory_monitor_config = script_home+"/monitor_memory.yaml"
    dbfile = script_home+"/monitoring.db"
    db_handler=DbHandler(dbfile)
    # Loading the monitor_disk.yaml data
    with open(memory_monitor_config, "r") as f:
        data = yaml.safe_load(f)
        # return false if the asg name is not found
        for asgname in data["ASG_NAME"]:
            startProcessing(asgname,data["region_name"],data["Namespace"],data["Metricname"],data["hosttemplatepath"],data["icingahostfilepath"],db_handler)


    db_handler.close_connection()


if __name__ == "__main__":
    main()