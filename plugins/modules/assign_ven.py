from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: respiro.illumio.assign_ven

short_description: This is the module to assign VEN to a workloads

version_added: "1.0.1"

description: This module lets user to add managed workload to PCE. First the csv file containing workload information is
read and script is run in the machine to install ven. Then the managed workload is matched with the machines from csv
file and appropriate labels are given.

options:
    user:
        description: This takes the user key value to access Illumio API
        required: true
        type: str
    password:
        description: This takes the user secret key to access Illumio API
        required: true
        type: str
    pce:
        description: This takes the url link to Illumio PCE
        required: true
        type: str
    org-href:
        description: This takes the organisation href for Illumio PCE
        required: true
        type: str
    workload:
        description: This takes the path to csv file contatining workload information
        required: true
        type: str
    linux_script:
        description: This is the path to file containing linux pairing script that can be geretated from PCE
        required: true
        type: str
    win_script:
        description: This is the path to file containing windows pairing script that can be generated from PCE
        required: true
        type: str

author:
    - Safal Khanal (@Safalkhanal)
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  respiro.illumio.assign_ven:
    user: "testusername"
    password: "testpassword"
    pce: "https://poc1.illum.io"
    org_href: "orgs/85"
    workload: 'workload.csv'
    linux_script : 'linuxPairing.sh'
'''

RETURN = r'''
original_message:
    type: str
    returned: always
    sample: {
         "msg": {
            "changed": true,
            "deployed": [
                "192.128.28.13"
            ],
            "failed": false,
            "not_deployed": [
                "192.128.28.34"
            ],
        }
    }

'''

from ansible.module_utils.compat.paramiko import paramiko
from pypsexec.client import Client
from ansible.module_utils.basic import AnsibleModule
import csv
import json
import aiohttp
import asyncio


def run_module():
    module_args = dict(
        workload=dict(type='str', required=True),
        linux_script=dict(type='str', required=False),
        win_script=dict(type='str', required=False),
        user=dict(type='str', required=True),
        password=dict(type='str', required=True),
        pce=dict(type='str', required=True),
        org_href=dict(type='str', required=True),
    )
    result = dict()
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    workload = module.params['workload']
    linux_script = module.params['linux_script']
    win_script = module.params['win_script']
    user = module.params["user"]
    password = module.params["password"]
    org_href = module.params["org_href"]
    pce = module.params["pce"]
    API = pce + "/api/v2/" + org_href + "/workloads?managed=true"
    labels_API = pce + "/api/v2/" + org_href + "/labels"
    list = {}
    list["deployed"] = []
    list["not_deployed"] = []

    if module.check_mode:
        module.exit_json(**result)

    # Function to pair linux workload to PCE
    def linux_pairing(public_ip, ssh_user, ssh_password):
        with open(linux_script) as f:
            s = f.read()
            values = s.split('&& ')

        # Execute script one line at a time
        for items in values:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                ssh.connect(public_ip, username=ssh_user, password=ssh_password)
            except (TimeoutError, OSError) as e:
                list["not_deployed"].append(public_ip)
                # when ssh is unsuccessful, returns with the public_ip address of that host
                return list
            if items == 'umask 026 ' or items == '/opt/illumio_ven_data/tmp/pair.sh':
                stdin, stdout, stderr = ssh.exec_command(items)
            else:
                stdin, stdout, stderr = ssh.exec_command('sudo ' + items)
            out = stdout.read().decode().strip()
            error = stderr.read().decode()
            ssh.close()
            list["deployed"].append(public_ip)
        return list

    # Function to pair windows workload to PCE (Under development)
    def win_pairing(public_ip, ssh_user, ssh_password):
        list["not_deployed"].append(public_ip)
        return list

    # Main code: Checks user supplied csv file, pairs those workloads, check labels in pce, and assign labels to worloads
    deployed = []
    not_deployed = []
    # getting data from the csv file and do the required operations
    with open(workload, 'r') as details:
        workload_details = csv.DictReader(details, delimiter=",")
        for rows in workload_details:
            public_ip = rows["ip"]
            ssh_user = rows["username"]
            ssh_password = rows["password"]
            os = rows['os']

            # Function to pair Linux machines to PCE
            if os == 'linux' or os == 'Linux' or os == 'lin' or os == 'Lin':
                finished_workload = linux_pairing(public_ip, ssh_user, ssh_password)
            elif os == 'windows' or os == 'Windows' or os == 'win' or os == 'Win':
                finished_workload = win_pairing(public_ip, ssh_user, ssh_password)
                
            # check finished workload list and find unique host addess
            for x in finished_workload["deployed"]:
                if x not in deployed:
                    deployed.append(x)

            for y in finished_workload["not_deployed"]:
                if y not in not_deployed:
                    not_deployed.append(y)

        module.exit_json(changed=True, deployed=deployed, not_deployed=not_deployed)


def main():
    run_module()


if __name__ == '__main__':
    main()
