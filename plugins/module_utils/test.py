from labels import *
from credential import Credential
import json

cred = Credential("api_1eb07e9cd9b3f918b", "c898ef78e305dc91d4239a1374746d9abbe86a655934328194c8dff7d12fa162", "poc1.illum.io" ,
                  "/orgs/50"
                  )
# create_label(cred, "role", "for_fun")
# get_labels(cred)
response = get_labels(cred)
data = json.loads(response.content.decode('utf-8'))
for label in data:
    print("href: " + label['href'])
    print("type: " + label['key'])
    print("name: " + label['value'])
    print("")
