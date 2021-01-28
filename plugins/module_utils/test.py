# from labels import *
from workloads import *
from credential import Credential
import json

cred = Credential("api_1eb07e9cd9b3f918b", "c898ef78e305dc91d4239a1374746d9abbe86a655934328194c8dff7d12fa162", "poc1.illum.io" ,
                  "/orgs/50"
                  )

# create_label(cred, "role", "for_fun")

# get_labels(cred)

# response = get_labels(cred)
# data = json.loads(response.content.decode('utf-8'))
# for label in data:
#     print("href: " + label['href'])
#     print("type: " + label['key'])
#     print("name: " + label['value'])
#     print("")

response = get_workloads(cred)
data = json.loads(response.content.decode('utf-8'))
for workload in data:
    print("href: " + workload['href'])
    print("hostname: " + workload['hostname'])
    if workload['public_ip'] is not None:
        print("public ip: " + workload['public_ip'])
    print("")

# update_workload(cred, "/orgs/50/workloads/250d0c9b-221a-4fdd-8897-3cd2df8fc6b9", {'hostname':"new.wee"})