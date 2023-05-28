import yaml
import os

script_home = os.path.dirname(os.path.abspath(__file__))
cpumonconfig = script_home + "/monitor_cpu.yaml"
with open(cpumonconfig, "r") as f:
    data = yaml.safe_load(f)
    for x in data['ASG_NAME']:
        print(x)