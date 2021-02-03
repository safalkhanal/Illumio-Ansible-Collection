#!/usr/bin/env python3

"""
Operations with workloads:
- Get workloads
- Update a workload's details
- Create unmanaged workload
"""

__author__ = "Nghia Huu (David) Nguyen"
__copyright__ = "Copyright 2021"
__credits__ = ["David Nguyen"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "David Nguyen"
__email__ = "davidnguyen0207@gmail.com"
__status__ = "In Development"

# Import required modules
from ansible_collections.respiro.illumio.plugins.module_utils.api_calls import sync_api, async_api


# Get all workloads from PCE
# Required credential
def get_workloads(creds):
    response = sync_api(creds, "get", "/workloads?max_result=1", True)
    num_items_in_return_set = int(response.headers['X-Total-Count'])
    if num_items_in_return_set >= 500:
        response = async_api(creds, "/workloads", True)
    return response


# Update workload's details
# Required credential, the href of the target workload
# And the payload containing the information that needs to be changed
def update_workload(creds, workload_href, payload):
    return sync_api(creds, "put", workload_href, False, payload)


# Create unmanaged workload
# Required a credential, name (display on PCE)
# A hostname, an IP
# And a set of label associated with the machine
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
    return sync_api(creds, "post", "/workloads", True, wl)
