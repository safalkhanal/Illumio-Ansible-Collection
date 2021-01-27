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
import time
import requests
from requests.auth import HTTPBasicAuth


# Making a synchronous API call
# For UNDER 500 items being queried on the server ("GET" operation)
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


# Making an asynchronous "GET" API request
# For OVER 500 items being queried on the server ("GET" operation)
# NOTE: only apply to "GET" HTTP operation and therefore doesn't require a http verb
# Requires a credential,
# Resource to access (e.g. /labels for labels),
# Does it contains the org_href or not
# And the data to push (unlikely to be used, since this will be a "GET" operation)
def async_api(creds, resource, has_org, payload=None):
    # Use different url depends on if the call requires an org_href
    if has_org:
        api_url = creds.url_with_org(resource)
    else:
        api_url = creds.url_with_api(resource)

    # Declare headers and timeout
    # IMPORTANT: "Prefer": "respond-async" on header
    headers = {"Prefer": "respond-async", "Content-type": "application/json", "Accept": "application/json"}
    timeout = 15

    # Make the call
    response = requests.request("get", api_url, auth=HTTPBasicAuth(creds.username, creds.auth_secret),
                                headers=headers, timeout=timeout, data=json.dumps(payload))

    # Since this is an asynchronous call so instead of the result,
    # The server will send back a special URL; We will perform GET operation on that URL
    # periodically until it's either success or fail

    # First we wait for suggested amount of time (provided by the server)
    time.sleep(int(response.headers['Retry-After']))

    # Then we query the second URL periodically until we get a confirmation
    status = ""
    monitor_url = response.headers['Location']
    while status != "done" and status != "failed":
        response = sync_api(creds, "get", monitor_url, False)
        status = json.loads(response.content)['status']
        time.sleep(1)

    # After the status on the second URL become "done"
    # The server will send us a third URL
    # Use the HREF to get results of the request
    response = sync_api(creds, "get", json.loads(response.content)['result']['href'], False)

    return response


