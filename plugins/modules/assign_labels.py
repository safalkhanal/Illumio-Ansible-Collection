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
    pce: "https://poc1.illum.io"
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
                "192.168.1.113"
            ],
            "not_assigned": [
                "19.16.1.111"
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
    org_id = module.params["org_id"]
    pce = module.params["pce"]
    API = pce + "/api/v2/orgs/" + org_id + "/workloads"
    labels_API = pce + "/api/v2/orgs/" + org_id + "/labels"
    list = {}
    list['assigned'] = []
    list['not_assigned'] = []

    if module.check_mode:
        module.exit_json(**result)

    # If the API data gets large(>500), async function is called
    async def async_api(api):
        async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(username, auth_secret)) as session:
            async with session.get(api) as resp:
                response = await resp.read()
        return response

    # Function to get the list of labels from PCE
    def display_labels():
        response = requests.get(labels_API, auth=HTTPBasicAuth(username, auth_secret))
        if len(response.content) == 500:
            response = async_api(labels_API)
        obj = json.loads(response.content)
        labels = dict()
        labels['role'] = dict()
        labels['app'] = dict()
        labels['env'] = dict()
        labels['loc'] = dict()
        for label_data in obj:
            if label_data['key'] == "role":
                labels['role'][label_data['value']] = label_data['href']
            if label_data['key'] == "app":
                labels['app'][label_data['value']] = label_data['href']
            if label_data['key'] == "env":
                labels['env'][label_data['value']] = label_data['href']
            if label_data['key'] == "loc":
                labels['loc'][label_data['value']] = label_data['href']
        return labels

    # Function to add labels to PCE
    def create_label(type, name):
        return requests.post(labels_API, auth=HTTPBasicAuth(username, auth_secret),
                             data=json.dumps({"key": type, "value": name})).content

    # Main code: Checks csv file and compares labels in pce and labels in csv file, and assign labels to worloads
    labels_details = display_labels()
    # getting data from the csv file and do the required operations
    with open(workload, 'r') as details:
        workload_details = csv.DictReader(details, delimiter=",")
        for rows in workload_details:
            public_ip = rows["ip"]
            role = rows['role']
            app = rows['app']
            env = rows['env']
            loc = rows['loc']

            # Get workloads from the PCE
            response = requests.get(API, auth=HTTPBasicAuth(username, auth_secret))
            obj = json.loads(response.text)

            # Check if label already exists in PCE. If not add to PCE and get its href.
            if role != "":
                if role in labels_details['role']:
                    role_href = labels_details['role'][role]
                else:
                    href = json.loads(create_label("role", role))['href']
                    labels_details['role'][role] = href
                    role_href = href
            else:
                role_href = ""
            if app != "":
                if app in labels_details['app']:
                    app_href = labels_details['app'][app]
                else:
                    href = json.loads(create_label("app", app))['href']
                    labels_details['app'][app] = href
                    app_href = href
            else:
                app_href = ""
            if env != "":
                if env in labels_details['env']:
                    env_href = labels_details['env'][env]
                else:
                    href = json.loads(create_label("env", env))['href']
                    labels_details['env'][env] = href
                    env_href = href
            else:
                env_href = ""
            if loc != "":
                if loc in labels_details['loc']:
                    loc_href = labels_details['loc'][loc]
                else:
                    href = json.loads(create_label("loc", loc))['href']
                    labels_details['loc'][loc] = href
                    loc_href = href
            else:
                loc_href = ""

            # Wait for the PCE to finish creating the new labels
            time.sleep(4.0)

            # check the workload from PCE with workload from csv file and assign labels
            check = 0
            for values in obj:
                for data in values['interfaces']:
                    if data['address'] == public_ip or values['public_ip'] == public_ip:
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
                        uri = pce + "/api/v2" + values['href']
                        response = requests.put(uri, auth=HTTPBasicAuth(username, auth_secret),
                                                data=json.dumps({'labels': label}))
                        list['assigned'].append(public_ip)
            if check == 0:
                list['not_assigned'].append(public_ip)
        module.exit_json(changed=True, labels_assigned=list['assigned'], not_assigned=list['not_assigned'])


def main():
    run_module()


if __name__ == '__main__':
    main()
