#!/usr/bin/env python

import re
import json
import os
import sys
import getopt
import requests
import warnings

warnings.filterwarnings("ignore")

def load_template_mapping ():
	lines = []
	with open("input_data") as f:
		lines = f.read().split('\n')
		
	return lines
	
def gettoken(ip,un,pw):
        url = "https://%s:8443/api/platform/login" % ip 
        headers={ 'Content-Type':'application/json' }
        payload = { 'username' : un, "password" : pw}
        response = requests.post(url,data=json.dumps(payload), headers=headers, verify=False, timeout=10)

        try:
                response = requests.post(url,data=json.dumps(payload), headers=headers, verify=False, timeout=10)
		
        except:
                print "Timeout getting to V2PC Master %s" % ip
                sys.exit(9)

        if response.status_code == 200:
                return response.json()['token']

        else:
                print "Could not get token for authentication, error code %s" % (response.status_code)
                sys.exit(9)

def add_template(template,ip,token,payload):

        url = "https://" + ip + ":8443/api/platform/do/v2/assetpublishtemplates/" + template
        headers = { 'Content-Type':'application/json', 'Authorization' : 'Bearer %s ' % token }

        response = requests.post(url,headers=headers, json=payload, verify=False, timeout=30)

        if response.status_code == 200:
                print "Publishing template %s created successfully!" % template

        else:
                print "Could not add template, error code %s" % (response.status_code)
                print response.json()['error']
                sys.exit(9)
def usage():
	print "Usage: " +  sys.argv[0] + " -i|--masterip <IP of V2PC master>"
    	print ""
    	print "-i|--masterip : IP Address of Master V2PC node"
	print "-h|--help     : Print this help message"
    	print ""
    	print ""
	sys.exit(9)

def main(argv):
        username = "admin"
        password = "default"

	if len(argv) == 0:
        	usage()

    	try:
        	opts,args = getopt.getopt(argv,"i:h",["masterip=","help"])
    	except getopt.GetoptError as err:
       	 	print str(err)
        	sys.exit(2)
    	else:
        	for opt,arg in opts:
            		if opt in ("-h","--help"):
                		usage()
            		if opt in ("-i","--masterip"):
                		ip = arg

	try:
		ip
	except:
		print "Required paramter -i|--masterip not passed"
		sys.exit(9)

	token = gettoken(ip,username,password)
	newtemplates = load_template_mapping()
	os.chdir('pubtemp')
	
	for templates in newtemplates:
		t = templates.split(',')
		template_name = t[0]
		file_name = t[1]
		kms_template = t[2]
	
		with open(file_name + '.json') as data_file:    
    			data = json.load(data_file)
			del data['transactionId']		
			del data['modified']		
			del data['id']		
			del data['externalId']		
			data['name'] = template_name

			# Add KMS template name if encrypted
			if kms_template != 'none':
				data['properties']["keyProfileRef"] = "smtenant_0.smkeyprofile.%s" % kms_template
				data['properties']["httpHeaderPolicyRef"] = "smtenant_0.smhttpheaderpolicy.default"
			add_template(template_name,ip,token,data)


if __name__ == '__main__':
    main(sys.argv[1:])
