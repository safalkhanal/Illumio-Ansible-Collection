from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: respiro.illumio.assign_labels

short_description: This is the module to assign/edit labels to workloads from the csv file.

version_added: "1.0.2"

description: This module assigns labels to workloads. First the csv file is read and workloads from
csv file is compared to workloads in PCE and labels are assigned to those workloads.

options:
    username:
        description: This takes the user key value to access Illumio API
        required: true
        type: str
    auth_secret:
        description: This takes the API secret key to access Illumio API
        required: true
        type: str
    pce:
        description: This takes the url link to Illumio PCE
        required: true
        type: str
    org_id:
        description: This takes the organisation ID for Illumio PCE
        required: true
        type: str
    workload:
        description: This takes the path to csv file containing workload information
        required: true
        type: str

author:
    - Safal Khanal (@Safalkhanal)
    - Nghia Huu (David) Nguyen (@DAVPFSN)
'''

EXAMPLES = r'''
- name: Test with a message
  respiro.illumio.assign_labels:
    username: "testusername"
    auth_secret: "testpassword"
    pce: "poc1.illum.io"
    org_id: "85"
    workload: 'workload.csv'
'''

RETURN = r'''
original_message:
    type: str
    returned: always
    sample: {
         "msg": {
            "changed": true,
            "failed": false,
            "labels_assigned": [
                "success.com"
            ],
            "not_assigned": [
                "fail.com"
            ],
        }
    }
'''

from ansible.module_utils.compat.paramiko import paramiko
from ansible.module_utils.basic import AnsibleModule
import time
import csv
import json
import requests
import aiohttp
import asyncio
from requests.auth import HTTPBasicAuth

# Import helper modules
from ansible_collections.respiro.illumio.plugins.module_utils.credential import Credential
from ansible_collections.respiro.illumio.plugins.module_utils.labels import create_label, create_label_href_dict
from ansible_collections.respiro.illumio.plugins.module_utils.workloads import get_workloads, update_workload


def run_module():
    module_args = dict(
        workload=dict(type='str', required=True),
        username=dict(type='str', required=True),
        auth_secret=dict(type='str', required=True),
        pce=dict(type='str', required=True),
        org_id=dict(type='str', required=True),
    )
    result = dict()
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    workload = module.params['workload']
    username = module.params["username"]
    auth_secret = module.params["auth_secret"]
    org_href = "/orgs/" + module.params["org_id"]
    pce = module.params["pce"]
    list = {'assigned': [], 'not_assigned': []}

    # Initialize new credential
    cred = Credential(username, auth_secret, pce, org_href)

    if module.check_mode:
        module.exit_json(**result)

    # Main code: Checks csv file and compares labels in pce and labels in csv file, and assign labels to worloads
    labels_details = create_label_href_dict(cred)
    # getting data from the csv file and do the required operations
    with open(workload, 'r') as details:
        workload_details = csv.DictReader(details, delimiter=",")
        for rows in workload_details:
            hostname = rows["hostname"]
            role = rows['role']
            app = rows['app']
            env = rows['env']
            loc = rows['loc']

            # Get workloads from the PCE
            response = get_workloads(cred)
            workloads_list = json.loads(response.text)

            # Check if label already exists in PCE. If not add to PCE and get its href.
            if role != "":
                if role in labels_details['role']:
                    role_href = labels_details['role'][role]
                else:
                    href = json.loads(create_label(cred, "role", role).content)['href']
                    labels_details['role'][role] = href
                    role_href = href
            else:
                role_href = ""
            if app != "":
                if app in labels_details['app']:
                    app_href = labels_details['app'][app]
                else:
                    href = json.loads(create_label(cred, "app", app).content)['href']
                    labels_details['app'][app] = href
                    app_href = href
            else:
                app_href = ""
            if env != "":
                if env in labels_details['env']:
                    env_href = labels_details['env'][env]
                else:
                    href = json.loads(create_label(cred, "env", env).content)['href']
                    labels_details['env'][env] = href
                    env_href = href
            else:
                env_href = ""
            if loc != "":
                if loc in labels_details['loc']:
                    loc_href = labels_details['loc'][loc]
                else:
                    href = json.loads(create_label(cred, "loc", loc).content)['href']
                    labels_details['loc'][loc] = href
                    loc_href = href
            else:
                loc_href = ""

            # Wait for the PCE to finish creating the new labels
            # This is just a fail-safe
            # Might not be necessary
            time.sleep(4.0)

            # check the workload from PCE with workload from csv file and assign labels
            check = 0
            for workload in workloads_list:
                if workload['hostname'] == hostname:
                    check = 1
                    label = []
                    if role_href:
                        label.append({"href": role_href})
                    if app_href:
                        label.append({"href": app_href})
                    if env_href:
                        label.append({"href": env_href})
                    if loc_href:
                        label.append({"href": loc_href})
                    update_workload(cred, workload['href'], {'labels': label})
                    list['assigned'].append(hostname)
            if check == 0:
                list['not_assigned'].append(hostname)
        module.exit_json(changed=True, labels_assigned=list['assigned'], not_assigned=list['not_assigned'])


def main():
    run_module()


if __name__ == '__main__':
    main()
