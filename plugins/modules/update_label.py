#!/usr/bin/env python3

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r'''
---
module: respiro.illumio.update_label

short_description: This module can update existing label's name on PCE

version_added: "1.1.0"

description: When executed, the module will use the provided label ID to try to retrieve the
current label's name. If successful, it will try to update the label's name to the new value 
supplied by the user; else, it will report a failure with a message that points out the most
likely cause of the error

options:
    pce:
        description: This takes the hostname from the URL link to Illumio PCE
        required: true
        type: str
    port:
        description:
            - The port number
            - Default to 443
        required: false
        type: str
    org_id:
        description: This takes the organisation ID for Illumio PCE
        required: true
        type: str
    label_id:
        description: This takes the label ID that needs to be updated
        required: true
        type: str
    username:
        description: This takes the user key value to access Illumio API. Generate the API key from PCE 
        and place the Authentication Username here
        required: true
        type: str
    auth_secret:
        description: This takes the user passkey to access Illumio API. From API key, place the Secret value here
        required: true
        type: str
    new_value:
        description: This takes the new value that the user want the label's name to be updated to
        required: true
        type: str
    
author:
    - Nghia Huu (David) Nguyen (@DAVPFSN)
'''

EXAMPLES = r'''
# Pass in a new label's value
- name: Test with a new value
  respiro.illumio.update_label:
    pce: "pod.someorganisation.com"
    port: "8443"
    org_id: "9"
    label_id: "65821"
    username: "someuser"
    auth_secret: "somesecret"
    new_value: "HelloWorld"

# fail the module
- name: Test failure of the module
  respiro.illumio.update_label:
    pce: "pod.someorganisation.com"
    port: "8443"
    org_id: "9"
    label_id: "wronglabelid"
    username: "someuser"
    auth_secret: "somesecret"
    new_value: "HelloWorld"
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
changed:
    description: Determine whether a change has been made or not
    type: bool
    returned: always
    sample: true
failed:
    description: Determine whether the module has ran successfully or has encountered an error
    type: bool
    returned: always
    sample: true
msg:
    description: Let the user know when an error has occurred and the most likely causes of failure
    type: str
    returned: When an error has occurred
    sample: "Connection error!! Make sure your pce is correct."
new:
    description: Let the user know what changes can be made
    type: str
    returned: Only when the module run successfully in check mode
    sample: "Change can be made to label's name from testing_8 to testing_9"
ok:
    description: Let the user know that no change is required
    type: str
    returned: When the module run successfully but the value is already up-to-date
    sample: "Current label's name is already the same as input value. Additional change is not required."
success:
    description: Let the user know the operation is successful
    type: str
    returned: When the label has been updated successfully
    sample: "Successfully update abc1 to abc2"
'''

from ansible.module_utils.basic import AnsibleModule
import json
from requests.exceptions import ConnectionError, Timeout

# Import helper modules
from ansible_collections.respiro.illumio.plugins.module_utils.credential import Credential
from ansible_collections.respiro.illumio.plugins.module_utils.labels import get_label, update_label


def run_module():
    # Define available arguments/parameters a user can pass to the module
    module_args = dict(
        pce=dict(type='str', required=True),
        port=dict(type='str', required=False, default='443'),
        org_id=dict(type='str', required=True),
        label_id=dict(type='str', required=True),
        username=dict(type='str', required=True),
        auth_secret=dict(type='str', required=True),
        new_value=dict(type='str', required=True)
    )

    # Initialise result dictionary to be passed back to the user
    result = dict(
        changed=False,
    )

    # Required to work with Ansible
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # Extract parameters from AnsibleModule object
    pce = module.params['pce']
    port = module.params['port']
    org_href = "/orgs/" + module.params['org_id']
    label_href = org_href + "/labels/" + module.params['label_id']
    username = module.params['username']
    auth_secret = module.params['auth_secret']
    new_value = module.params['new_value']

    # Initialise new credential
    cred = Credential(username, auth_secret, pce, org_href, port)

    # Construct request payload
    data = {"value": new_value}

    try:

        # Check to see if the label exists
        response_get = get_label(cred, label_href)

        # If label exists
        # Check if the current value is the same as input value
        # If yes then exit
        # If no then update
        if response_get.status_code == 200:
            current_value = json.loads(response_get.content)['value']
            if current_value == new_value:
                module.exit_json(ok="Current label's name is already the same as input value. "
                                    "Additional change is not required.", **result)
            else:
                # In check mode
                # Return changes to be made without actually making the changes
                if module.check_mode:
                    module.exit_json(new="Change can be made to label's name"
                                         " from {} to {}".format(current_value, new_value))
                # Make label update request to the API
                response_put = update_label(cred, label_href, data)
                # If update is successful
                if response_put.status_code == 204:
                    result['changed'] = True
                    result['success'] = "Successfully update {} to {}".format(current_value, new_value)
                    module.exit_json(**result)
                # If failed
                else:
                    result['response'] = response_put.status_code
                    module.fail_json(msg="All information provided is correct and the server responded. "
                                         "There are changes to be made from {} to {} but the operation "
                                         "was unable to be completed".format(current_value, new_value), **result)
        # Errors handling
        # Unable to check for label's existence
        elif response_get.status_code == 404:
            module.fail_json(msg="Label doesn't exist.", **result)
        elif response_get.status_code == 401:
            module.fail_json(msg="Wrong login credentials.", **result)
        elif response_get.status_code == 403:
            module.fail_json(msg="The data is valid and understood but is denied by the server. "
                                 "Most likely caused by a wrong org_id.", **result)
        else:
            module.fail_json(msg="Error occurred when requesting API.", **result)

    except Timeout as e:
        module.fail_json(msg="Connection timeout. Please check your internet connection or port number.", **result)
    except ConnectionError as e:
        module.fail_json(msg="Fail to establish a connection. Make sure your pce is correct.", **result)
    except Exception as e:
        module.fail_json(msg="Fail due to unexpected issue.", **result)


def main():
    run_module()


if __name__ == '__main__':
    main()
