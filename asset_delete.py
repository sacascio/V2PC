#!/usr/bin/env python

import re
import json
import os
import sys
import getopt
import requests
import warnings
import time

warnings.filterwarnings("ignore")

def delete_asset(ip,asset,wf):
        url = "https://" + ip + ":7001/v1/assetworkflows/" + wf + "/assets/" + asset
        response = requests.delete(url, verify=False, timeout=30)

        if response.status_code == 202:
                print "Asset %s successfully deleted!" % asset

        else:
                print "Could not delete asset %s, error code %s" % (asset,response.status_code)
                print response.json()['error']
                sys.exit(9)
def usage():
	print "Usage: " +  sys.argv[0] + " -i|--amip <IP of AM>"
    	print ""
    	print "-i|--amip : IP Address of AM V2PC node"
    	print "-w|--workflow : Workflow Name"
	print "-h|--help     : Print this help message"
    	print ""
    	print ""
	sys.exit(9)

def main(argv):

	if len(argv) == 0:
        	usage()

    	try:
        	opts,args = getopt.getopt(argv,"i:w:h",["amip=","workflow=","help"])
    	except getopt.GetoptError as err:
       	 	print str(err)
        	sys.exit(2)
    	else:
        	for opt,arg in opts:
            		if opt in ("-h","--help"):
                		usage()
            		if opt in ("-i","--amip"):
                		ip = arg
            		if opt in ("-w","--workflow"):
                		wf = arg

	try:
		ip
	except:
		print "Required paramter -i|--amip not passed"
		sys.exit(9)
	
	try:
		wf
	except:
		print "Required paramter -w|--workflow not passed"
		sys.exit(9)

	with open('500assets') as f:
                lines = f.read().splitlines()

	for a in lines:
		delete_asset(ip,a,wf)
		time.sleep(120)
	

if __name__ == '__main__':
    main(sys.argv[1:])
