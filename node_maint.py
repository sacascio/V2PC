#!/usr/bin/env python

import json
import sys
import warnings
import requests
import getopt
import time
import os

warnings.filterwarnings("ignore")

def increment_ts(curtime):
	os.environ['TZ']= 'UTC'
	pattern = '%Y-%m-%dT%H:%M:%S.%fZ'
	epoch = int(time.mktime(time.strptime(curtime,pattern)))
	epoch = epoch + 1
	ntime = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.localtime(epoch))	
	return ntime

def prepare_aic(sysdata,fname):
	with open(fname) as f:
		lines = f.readlines()
		for node in lines:
			node = node.strip()	
			if node not in sysdata:
				print "Node %s in input file does not exist in V2PC or is not an MPE or MCE.  Exiting" % node
			else:
				for aic in sysdata[node]:
					sysdata[node][aic]['modify'] = True
	return sysdata				

def get_node_list(ip,token):
	rdata = {}
        url = "https://%s:8443/api/platform/do/v2/regions/region-0/appinstances" % (ip)
        headers = { 'Content-Type':'application/json', 'Authorization' : 'Bearer %s ' % token }
        response = requests.get(url,headers=headers, verify=False, timeout=30)
	
	if response.status_code == 200:
                data = response.json()
		
		for t in data:
			instname =  t['name']
			insttype =  t['properties']['type']
			if insttype != 'cisco-ce' and insttype != 'cisco-pe':
				continue

			for apps in t['properties']['applications']:
				if apps != 'mpe' and apps != 'mce':
					continue

				for ninfo in t['properties']['applications'][apps]['nodesInfo']:
					status   = ninfo['status']
					nodeName = ninfo['nodeName']
					state    = ninfo['state']
					smodtime = ninfo['stateModTime']
					rdata[nodeName] = {}
					rdata[nodeName][instname] = {}
					rdata[nodeName][instname] = { 'modify': False, 'status':status,'state':state,'stime':smodtime, 'app' : apps}
		return rdata

	else:
		print "Could not get node list, HTTP error code %s" % response.status_code

def execute_status_change(ip,token,aic,tdata,state):
        url = "https://%s:8443/api/platform/do/v2/regions/region-0/appinstances/%s" % (ip,aic)
        headers = { 'Content-Type':'application/json', 'Authorization' : 'Bearer %s ' % token }
        response = requests.put(url,headers=headers, data=json.dumps(tdata),verify=False, timeout=30)
       	
	if response.status_code == 200:
		print "OK: Nodes in AIC %s updated to %s" % (aic,state.lower())
	else:
		print "ERROR: Nodes in AIC %s not moved to %s, HTTP code %s" % (aic,state.lower(),response.status_code)
		

def usage():
        print "Usage: " +  sys.argv[0] + " -i|--masterip <IP of V2PC master>" + " -f|--file file" + " -s|--status" 
        print ""
        print "-i|--masterip : IP Address of Master V2PC node"
        print "-f|--file     : Filename with a list of nodes to enable/disable"
        print "-s|--status   : Must be set to enable or disable"
        print "-h|--help     : Print this help message"
        print ""
        print ""
        sys.exit(9)


def gettoken(ip,un,pw):

	url = "https://%s:8443/api/platform/login" % ip
	headers={ 'Content-Type':'application/json' }
	payload = { 'username' : un, "password" : pw}
	try:
		response = requests.post(url,data=json.dumps(payload), headers=headers, verify=False, timeout=10)
	except:
		print "Timeout getting to V2PC Master"
		sys.exit(9)
	
	if response.status_code == 200:
        	return response.json()['token']
    
    	else:
        	print "Could not get token for authentication, error code %s" % (response.status_code)
        	sys.exit(9)

def change_status(ip,token,sysdata,status):
	aicd = {}
	execute_put = 0

	for node in sysdata:
		for aic in sysdata[node]:
			if sysdata[node][aic]['modify'] is True:
				aicd[aic] = sysdata[node][aic]['app']

	for aic in aicd:
		url = "https://%s:8443/api/platform/do/v2/regions/region-0/appinstances/%s" % (ip,aic)
		headers = { 'Content-Type':'application/json', 'Authorization' : 'Bearer %s ' % token }

		response = requests.get(url,headers=headers, verify=False, timeout=30)
	
		if response.status_code == 200:
                	data = response.json()
	
			for node in sysdata:
				for aic_t in sysdata[node]:
					if aic == aic_t:
						if sysdata[node][aic]['modify'] is True:
							for t in data['properties']['applications'][aicd[aic]]['nodesInfo']:
								if t['nodeName'].lower() == node.lower():
									if status.lower() == t['state'].lower():
										print "Node %s already set to %s" % (node,status.lower())
									else:
										print "Changing status of node %s to %s" % (node,status.lower())
										execute_put = 1
										tsplus1 = increment_ts(t['stateModTime'])
										t['state'] = status.lower()
										if status.lower() == 'disable':
											t['status'] = 'Inactive'
										else:
											t['status'] = 'Active'
										t['stateModTime'] = tsplus1
			if execute_put == 1:		
				execute_status_change(ip,token,aic,data,status) 
				execute_put = 0	
			else:
				print "No changes made to AIC %s, skipping execute..." % aic

        	else:
               		print "Could not get AIC %s, node %s error code %s" % (aic,node,response.status_code)
                	sys.exit(9)

def main(argv):
	
	if len(argv) == 0:
                usage()

	username = "admin"
	password = "default"

        try:
                opts,args = getopt.getopt(argv,"i:a:f:s:t:h",["masterip=","file=","status=","help"])
        except getopt.GetoptError as err:
                print str(err)
                sys.exit(2)
        else:
                for opt,arg in opts:
                        if opt in ("-h","--help"):
                                usage()
                        if opt in ("-i","--masterip"):
                                ip = arg
                        if opt in ("-f","--file"):
                                fname = arg
				if not(os.path.isfile(fname)):
					print "File %s passed in with %s option doesn't exist.  Exiting" % (fname,opt)
                        if opt in ("-s","--status"):
                                status = arg

        try:
                ip
        except:
                print "Required paramter -i|--masterip not passed"
                sys.exit(9)
        
	try:
                fname
        except:
                print "Required paramter -f|--file not passed"
                sys.exit(9)

	try:
                status
        except:
                print "Required paramter -s|--status not passed"
                sys.exit(9)
	else:
		if status.lower() != 'disable' and status.lower() != 'enable':
			print "Status must be disable or enable..exiting"
			sys.exit(9)
	
	token = gettoken(ip,"admin","default")
	sysdata = get_node_list(ip,token)
	sysdata = prepare_aic(sysdata,fname)
	change_status(ip,token,sysdata,status)
	print "DONE...."

if __name__ == '__main__':
    main(sys.argv[1:])
