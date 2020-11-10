from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: display_label_info

short_description: This is the module to display Illumio labels


description: Use this module to get the list of labels in yout illumio. This module can either fetch data for individual
 sets of labels or fetch all the labels data.

options:
    user:
        description: This takes the user key value to access Illumio API. Generate the API key from PCE and place the Authentication Username here.
        required: true
        type: str
    password:
        description: This takes the user passkey to access Illumio API. From API key, place the Secret value here
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
    type:
        description:
            - type of label that you want to display ('all', 'env', 'loc', 'app', 'role').
        required: true
        type: str

# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - my_namespace.my_collection.my_doc_fragment_name

author:
    - Safal Khanal (@safalkhanal99)
'''

EXAMPLES = r'''
  tasks:
    - name: display all labels in PCE
      respiro.illumio.display_label_info:
        type: "all"
        user: "{{login}}"
        password: "{{password}}"
        pce: "{{pce}}"
        org_href: "{{org_href}}"
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.

description: json list of labels
type: json
returned: always
sample:
    {
    "msg": {
        "changed": true,
        "failed": false,
        "meta": [
            {
                "created_at": "2018-09-06T06:52:49.817Z",
                "created_by": {
                    "href": "/users/45"
                },
                "href": "/orgs/5/labels/57",
                "key": "loc",
                "updated_at": "2018-09-06T06:52:49.817Z",
                "updated_by": {
                    "href": "/users/45"
                },
                "value": "location1"
            },
        }
    }
'''

from ansible.module_utils.basic import AnsibleModule
import json
import asyncio
import requests
import aiohttp
from requests.auth import HTTPBasicAuth


async def async_api(api, user, password):
    async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(user, password)) as session:
        async with session.get(api) as resp:
            response = await resp.read()
    return response


def run_module():
    TYPE = ['all', 'env', 'loc', 'app', 'role']

    module_args = dict(
        type=dict(type='str', required=True),
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
    API = module.params["pce"] + "/api/v1/" + module.params["org_href"] + "/labels"
    if module.check_mode:
        module.exit_json(**result)
    checksum = 0
    for label_type in TYPE:
        if (module.params['type'] == label_type):
            checksum = 1
            break
    if checksum == 0:
        module.fail_json(msg="Error!! Invalid label type.")

    try:
        response = requests.get(API, auth=HTTPBasicAuth(module.params["user"], module.params["password"]))
        if len(response.content) == 500:
            response = async_api(API, module.params["user"], module.params["password"])
        obj = json.loads(response.text)
        list = []
        for values in obj:
            if values['key'] == module.params["type"]:
                list.append(values)
            elif module.params["type"] == 'all':
                list.append(values)
        module.exit_json(changed=True, meta=list)

    except Exception as e:
        module.fail_json(msg="Error. Could not connect to PCE. This may be due to wrong credentials!!")


def main():
    run_module()


if __name__ == '__main__':
    main()
