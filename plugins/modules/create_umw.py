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
        description: This takes the api secret key to access Illumio API. From API key, place the Secret value here
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
# Pass in a message
- name: Test with a path to csv file
  respiro.illumio.create_umw:
    username: "api_12321323cf4545"
    auth_secret: "097jhdjksb9387384hjd3384bnfj93"
    pce: "poc1.illum.io"
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

# Import helper modules
from ansible_collections.respiro.illumio.plugins.module_utils.credential import Credential
from ansible_collections.respiro.illumio.plugins.module_utils.labels import create_label, create_label_href_dict
from ansible_collections.respiro.illumio.plugins.module_utils.workloads import create_umw


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
    org_href = "/orgs/" + module.params["org_id"]
    pce = module.params["pce"]

    cred = Credential(login, auth_secret, pce, org_href)
    labels_details = create_label_href_dict(cred)
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
                    href = json.loads(create_label(cred, "role", role).content)['href']
                    labels_details['role'][role] = href
                    role = href
            else:
                role = ""
            if app is not "":
                if app in labels_details['app']:
                    app = labels_details['app'][app]
                else:
                    href = json.loads(create_label(cred, "app", app).content)['href']
                    labels_details['app'][app] = href
                    app = href
            else:
                app = ""
            if env is not "":
                if env in labels_details['env']:
                    env = labels_details['env'][env]
                else:
                    href = json.loads(create_label(cred, "env", env).content)['href']
                    labels_details['env'][env] = href
                    env = href
            else:
                env = ""
            if loc is not "":
                if loc in labels_details['loc']:
                    loc = labels_details['loc'][loc]
                else:
                    href = json.loads(create_label(cred, "loc", loc).content)['href']
                    labels_details['loc'][loc] = href
                    loc = href
            else:
                loc = ""

            # Wait for the PCE to finish creating the new labels
            # This is just a fail-safe
            # Might not be necessary
            time.sleep(4.0)

            create_umw(cred, name, hostname, ip, role, app, env, loc)
    module.exit_json(changed=True, meta='Workload added')


def main():
    run_module()


if __name__ == '__main__':
    main()
