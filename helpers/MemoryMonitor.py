#!/monitoringScripts/VENVT/bin/python
import boto3
import logging
from datetime import datetime, timedelta


class AsgMemoryMonitor:
    def __init__(self,):
        self.logger = self._create_logger()
    # constructor not needed


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

    def _get_memory_usage(self,instance_id,region_name,asg_name,namespace,metric_name):
        cloudwatch_client = boto3.client('cloudwatch',region_name=region_name)
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=5)
        response = cloudwatch_client.get_metric_data(
            MetricDataQueries=[
                {
                    'Id': 'memory_utilization',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': namespace,
                            'MetricName': metric_name,
                            'Dimensions': [
                                {
                                    'Name': 'InstanceId',
                                    'Value': instance_id
                                },
                            ]
                        },
                        'Period': 60,
                        'Stat': 'Average',
                    }
                },
            ],
            StartTime=start_time,
            EndTime=end_time,
        )
        data_points = response['MetricDataResults'][0]['Values']

        if data_points:
            memory_usage_percent = data_points[-1]
        else:
            memory_usage_percent = 1
        print(f"{memory_usage_percent}% used in {instance_id}")

def main():
    print("Use main")


if __name__ == "__main__":
    main()