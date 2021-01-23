from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: respiro.illumio.create_umw

short_description: This is the module to create unmanaged workloads in PCE

version_added: "1.0.8"

description: Use this module to add unmanaged workloads to PCE. pass the path to csv file containing workload information and assiciated label along with credentials to
PCE to add unmanaged workloads to PCE

options:
    username:
        description: This takes the user key value to access Illumio API. Generate the API key from PCE and place the Authentication Username here.
        required: true
        type: str
    auth_secret:
        description: This takes the api secret keyu to access Illumio API. From API key, place the Secret value here
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
        description: This takes the path to csv file contatining workload information
        required: true
        type: str

author:
    - Safal Khanal (@Safalkhanal)
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a path to csv file
  respiro.illumio.create_umw:
    username: "api_12321323cf4545"
    auth_secret: "097jhdjksb9387384hjd3384bnfj93"
    pce: "https://poc1.illum.io"
    org_id: "80"
    workload: "workload.csv"
'''

RETURN = r'''
# This is an examples of possible return value.
description: json list of labels
type: json
returned: always
sample:
    {
     "msg": {
        "changed": true,
        "failed": false,
        "meta": "Workload added",
     }
    }
'''

from ansible.module_utils.basic import AnsibleModule
import time
import json
import csv
import requests
import aiohttp
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
    login = module.params["username"]
    auth_secret = module.params["auth_secret"]
    org_id = module.params["org_id"]
    pce = module.params["pce"]

    class Creds(object):

        def __init__(self, login, auth_secret, pce, org):
            self.login = login
            self.auth_secret = auth_secret
            self.pce = pce
            self.org = org

        def url_with_api(self, rest):
            return self.pce + "/api/v2/" + rest

        def url_with_org(self, rest):
            return self.pce + "/api/v2/orgs/" + self.org + rest

    def sync_api(creds, type, resource, org, payload=None):
        if org:
            api = creds.url_with_org(resource)
        else:
            api = creds.url_with_api(resource)
        if type == "get":
            return requests.get(api, auth=HTTPBasicAuth(creds.login, creds.auth_secret))
        elif type == "post":
            return requests.post(api, auth=HTTPBasicAuth(creds.login, creds.auth_secret), data=payload)

    async def async_api(creds, type, resource, org, payload=None):
        if org:
            api = creds.url_with_org(resource)
        else:
            api = creds.url_with_api(resource)
        if type == "get":
            async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(creds.login, creds.auth_secret)) as session:
                async with session.get(api) as resp:
                    response = await resp.read()
        elif type == "post":
            async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(creds.login, creds.auth_secret)) as session:
                async with session.post(api, data=payload) as resp:
                    response = await resp.json()

        return response

    def display_labels():
        response = sync_api(creds, "get", "/labels", True)
        if len(response.content) == 500:
            response = async_api(creds, "get", "/labels", True)
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

    # add labels to pce
    def create_label(creds, type, name):
        return sync_api(creds, "post", "/labels", True, json.dumps({"key": type, "value": name})).content

    # Function to add unmanaged workloads to PCE
    def create_umw(creds, name, hostname, ip, label1=None, label2=None, label3=None, label4=None):
        label = []
        if label1:
            label.append({"href": label1})
        if label2:
            label.append({"href": label2})
        if label3:
            label.append({"href": label3})
        if label4:
            label.append({"href": label4})
        wl = {
            "name": name,
            "hostname": hostname,
            "public_ip": ip,
            "interfaces":
                [{"name": "eth0",
                  "address": ip,
                  "cidr_block": 32,
                  "link_state": "up"}],
            "online": True,
            "labels": label
        }
        return sync_api(creds, "post", "/workloads", True, json.dumps(wl))

    creds = Creds(login, auth_secret, pce, org_id)
    labels_details = display_labels()
    with open(workload, 'r') as details:
        workload_details = csv.DictReader(details, delimiter=",")
        for rows in workload_details:
            name = rows["name"]
            hostname = rows["hostname"]
            ip = rows["ip"]
            role = rows["role"]
            app = rows["app"]
            env = rows["env"]
            loc = rows["loc"]
            if role is not "":
                if role in labels_details['role']:
                    role = labels_details['role'][role]
                else:
                    href = json.loads(create_label(creds, "role", role))['href']
                    labels_details['role'][role] = href
                    role = href
            else:
                role = ""
            if app is not "":
                if app in labels_details['app']:
                    app = labels_details['app'][app]
                else:
                    href = json.loads(create_label(creds, "app", app))['href']
                    labels_details['app'][app] = href
                    app = href
            else:
                app = ""
            if env is not "":
                if env in labels_details['env']:
                    env = labels_details['env'][env]
                else:
                    href = json.loads(create_label(creds, "env", env))['href']
                    labels_details['env'][env] = href
                    env = href
            else:
                env = ""
            if loc is not "":
                if loc in labels_details['loc']:
                    loc = labels_details['loc'][loc]
                else:
                    href = json.loads(create_label(creds, "loc", loc))['href']
                    labels_details['loc'][loc] = href
                    loc = href
            else:
                loc = ""

            # Wait for the PCE to finish creating the new labels
            # This is just a fail-safe
            # Might not be necessary
            time.sleep(4.0)

            wl = create_umw(creds, name, hostname, ip, role, app, env, loc)
    module.exit_json(changed=True, meta='Workload added')


def main():
    run_module()


if __name__ == '__main__':
    main()
