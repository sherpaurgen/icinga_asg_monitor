import sqlite3,subprocess
from jinja2 import Template
from helpers.MainLogger import setup_logger

logger = setup_logger()


def generate_host_file(icingahostfilepath, hosttemplatepath):
    con = sqlite3.connect('icinga.db')
    cursor = con.cursor()
    cursor.execute('SELECT * FROM cpu_usage')
    rows = cursor.fetchall()
    with open(hosttemplatepath, 'r') as file:
        template_content = file.read()
    template = Template(template_content)
    for row in rows:
        rendered_template = template.render(hostname=row[2], address=row[3], asg_name=row[6], instance_id=row[1])
        with open(icingahostfilepath, 'a') as output_file:
            output_file.write(rendered_template)
        #(56, 'i-04678cd0a99c43075', 'Demoasg_i-04678cd0a99c43075', '52.39.213.223', '172.31.39.118', 0.0989988876529518, 'Demoasg', 'us-west-2', '2023-06-06 09:15:28')
    cursor.close()
    con.close()

def reloadIcinga():
    command1 = "/usr/sbin/icinga2 daemon -C > /dev/null 2>&1"
    try:
        subprocess.run(command1, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.warning(f"reloadIcinga: Command '{command1}' failed with exit code {e.returncode}")
    else:
        # Run the second command if the first command succeeded
        command2 = "sudo systemctl reload icinga2"
        # command2 = "echo"
        try:
            subprocess.run(command2, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            logger.warning(f"reloadIcinga: Command '{command2}' failed with exit code {e.returncode}")
        else:
            logger.warning("Icinga2 Reloaded Successfully")
