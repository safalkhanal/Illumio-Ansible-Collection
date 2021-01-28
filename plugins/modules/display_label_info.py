from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: respiro.illumio.display_label_info

version_added: "1.0.8"

short_description: This is the module to display Illumio labels


description: Use this module to get the list of labels in your illumio. This module can either fetch data for individual
 sets of labels or fetch all the labels data.

options:
    username:
        description: This takes the user key value to access Illumio API. Generate the API key from PCE and place the Authentication Username here.
        required: true
        type: str
    auth_secret:
        description: This takes the user secret key to access Illumio API. From API key, place the Secret value here
        required: true
        type: str
    pce:
        description: This takes the url link to Illumio PCE
        required: true
        type: str
    org-id:
        description: This takes the organisation ID for Illumio PCE
        required: true
        type: str
    type:
        description:
            - type of label that you want to display ('all', 'env', 'loc', 'app', 'role').
        required: true
        type: str

author:
    - Safal Khanal (@safalkhanal99)
    - Nghia Huu (David) Nguyen (@DAVPFSN)
'''

EXAMPLES = r'''
  tasks:
    - name: display all labels in PCE
      respiro.illumio.display_label_info:
        type: "all"
        username: "api_12321323cf4545"
        auth_secret: "097jhdjksb9387384hjd3384bnfj93"
        pce: "poc1.illum.io"
        org_id: "80"
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
        "meta": [
            {
                "created_at": "2018-09-06T06:52:49.817Z",
                "created_by": {
                    "href": "/users/45"
                },
                "href": "/orgs/80/labels/57",
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

# Import helper modules
from ansible_collections.respiro.illumio.plugins.module_utils.credential import Credential
from ansible_collections.respiro.illumio.plugins.module_utils.labels import get_labels


def run_module():
    TYPE = ['all', 'env', 'loc', 'app', 'role']

    module_args = dict(
        type=dict(type='str', required=True),
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

    username = module.params["username"]
    auth_secret = module.params["auth_secret"]
    pce = module.params["pce"]
    org_href = "/orgs/" + module.params["org_id"]
    input_type = module.params["type"]

    # Initialize new credential
    cred = Credential(username, auth_secret, pce, org_href)

    if module.check_mode:
        module.exit_json(**result)
    checksum = 0
    for label_type in TYPE:
        if (input_type == label_type):
            checksum = 1
            break
    if checksum == 0:
        module.fail_json(msg="Error!! Invalid label type.")

    try:
        response = get_labels(cred)
        obj = json.loads(response.text)
        list = []
        for values in obj:
            if values['key'] == input_type:
                list.append(values)
            elif input_type == 'all':
                list.append(values)
        module.exit_json(changed=True, success=list)

    except Exception as e:
        module.fail_json(msg="Error. Could not connect to PCE. This may be due to wrong credentials!!")


def main():
    run_module()


if __name__ == '__main__':
    main()
