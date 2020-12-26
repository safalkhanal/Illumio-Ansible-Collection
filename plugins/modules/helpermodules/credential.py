#!/usr/bin/env python3

"""
Declaring Credential object:
- Store login information: username, authentication secret
- PCE, port, org_href
"""

__author__ = "Nghia Huu (David) Nguyen"
__copyright__ = "Copyright 2020"
__credits__ = ["David Nguyen"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "David Nguyen"
__email__ = "davidnguyen0207@gmail.com"
__status__ = "In Development"


class Credential(object):

    # Initialise Credential
    # Default port is 443
    def __init__(self, username, auth_secret, pce, org_href, port="443"):
        self.username = username
        self.auth_secret = auth_secret
        self.pce = pce
        self.org_href = org_href
        self.port = port

    # For API call without org_href
    # "rest" mean the rest of the API call
    # e.g. /labels, /pairing_profiles,... depend on the task
    def url_with_api(self, rest):
        # remove "/" from user input to avoid "//example"
        if rest[0] == "/":
            rest = rest[1:]
        return "https://" + self.pce + ":" + self.port + "/api/v2/" + rest

    # For API call with org_href
    # "rest" mean the rest of the API call (or URI)
    # e.g. /labels, /pairing_profiles,... depend on the task
    def url_with_org(self, rest):
        # remove "/" from user input to avoid "//example"
        if rest[0] == "/":
            rest = rest[1:]
        return "https://" + self.pce + ":" + self.port + "/api/v2" + self.org_href + "/" + rest


