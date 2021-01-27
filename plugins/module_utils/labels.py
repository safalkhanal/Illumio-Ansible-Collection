#!/usr/bin/env python3

"""
Operations with labels:
- Create labels
- Get labels
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


# Create new label
# Required a credential, a label's type and label's name
def create_label(creds, type, name):
    return sync_api(creds, "post", "/labels", True, {"key": type, "value": name})


# Get all labels on PCE
# Required a credential
# Will also query for the number of results of data set
# Will use async request if the data set has >500 items
def get_labels(creds):
    response = sync_api(creds, "get", "/labels?max_result=1", True)
    num_items_in_return_set = int(response.headers['X-Total-Count'])
    if num_items_in_return_set >= 500:
        response = async_api(creds, "/labels", True)
    return response
