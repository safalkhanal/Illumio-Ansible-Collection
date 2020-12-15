from credential import Credential
from api_calls import async_api
import json

login = "api_1eb07e9cd9b3f918b"
passwd = "c898ef78e305dc91d4239a1374746d9abbe86a655934328194c8dff7d12fa162"
pce = "poc1.illum.io"
port = "443"
org_href = "/orgs/50"

cred = Credential(login, passwd, pce, org_href, port)
response = async_api(cred, "/labels/", True)
data = json.loads(response.content.decode('utf-8'))
for label in data:
    print("href: " + label['href'])
    print("type: " + label['key'])
    print("name: " + label['value'])
    print("")
