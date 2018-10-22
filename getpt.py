#!/usr/bin/env python

import sys
import json
import warnings
import requests

warnings.filterwarnings("ignore")

def gettoken(ip,un,pw):

        url = "https://%s:8443/api/platform/login" % ip
        headers={ 'Content-Type':'application/json' }
        payload = { 'username' : un, "password" : pw}

        try:
                response = requests.post(url,data=json.dumps(payload), headers=headers, verify=False, timeout=30)
        except:
                print "Timeout getting to V2PC Master"
                sys.exit(9)

        if response.status_code == 200:
                return response.json()['token']

        else:
                print "Could not get token for authentication, error code %s" % (response.status_code)
                sys.exit(9)

def gettemplates(ip,token,name):
	if name == 'none':
		url = "https://" + ip + ":8443/api/platform/do/v2/assetpublishtemplates"
	else:
		url = "https://" + ip + ":8443/api/platform/do/v2/assetpublishtemplates/" + name

	headers = { 'Content-Type':'application/json', 'Authorization' : 'Bearer %s ' % token }

	response = requests.get(url,headers=headers, verify=False, timeout=30)

	if response.status_code == 200:
                return response.json()

        else:
                print "Could not get token for authentication, error code %s" % (response.status_code)
                sys.exit(9)


def main(argv):
	username = "admin"
	password = "default"
	ip       = "10.105.178.5"

	token = gettoken(ip,"admin","default")
	templates  = gettemplates(ip,token,"none")
	for i in templates:
		name = i['name']
		f = open("backup_template/" + name + ".json","w")
		tplate  = gettemplates(ip,token,name)
		f.write(json.dumps(tplate))
		f.close()

if __name__ == '__main__':
    main(sys.argv[1:])
