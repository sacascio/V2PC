#!/usr/bin/env python
import json
import requests

headers = {'Content-type': 'application/json'}
url = 'https://s192.168.29.133/api/aaaLogin.json'

pay =  { "aaaUser" : { "attributes": {"name":"admin","pwd":"admin12345"} } }
payload =  json.dumps(pay)

response = requests.post(url, data=payload, headers=headers)

print response
