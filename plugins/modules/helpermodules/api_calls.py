#!/usr/bin/env python3

"""
Making calls to Illumio API
Included both Synchronous and Asynchronous version
"""

__author__ = "Nghia Huu (David) Nguyen"
__copyright__ = "Copyright 2020"
__credits__ = ["David Nguyen"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "David Nguyen"
__email__ = "davidnguyen0207@gmail.com"
__status__ = "In Development"

import json
import requests
from requests.auth import HTTPBasicAuth


# Making a synchronous API call
# For volume under 500
# Requires a credential, a http verb, resource to access (e.g. /labels for labels),
# Does it contains the org_href or not
# And the data to push
def sync_api(creds, http_verb, resource, has_org, payload=None):
    # Use different url depends on if the call requires an org_href
    if has_org:
        api_url = creds.url_with_org(resource)
    else:
        api_url = creds.url_with_api(resource)

    # Declare headers and timeout
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    timeout = 15

    # Make the call
    response = requests.request(http_verb, api_url, auth=HTTPBasicAuth(creds.username, creds.auth_secret),
                                headers=headers, timeout=timeout, data=json.dumps(payload))

    return response





