#!/usr/bin/env python3

"""
Operations with workloads:
- Get workloads
- Update a workload's details
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
