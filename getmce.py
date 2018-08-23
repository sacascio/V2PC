#!/usr/bin/env python

import getopt
import requests
import sys
import warnings
import json
warnings.filterwarnings("ignore")

def usage():
        print "Usage: " +  sys.argv[0] + " -i|--am <IP of AM node>"
        print ""
        print "This script prints out the MCE"
        print ""
        print "-i|--amip : IP Address of AM node"
        print "-w|--wf   : Workflow Name"
        print "-h|--help     : Print this help message"
        print ""
        print ""
        sys.exit(9)

def getsvcinfo(amip,wf):
        url = "https://" + amip + ":7001/v1/assetworkflows/" + wf + "/assets/"

        headers = { 'Content-Type':'application/json' }

        response = requests.get(url,headers=headers, verify=False, timeout=30)

        if response.status_code == 200:
                return response.json()

        else:
                print "Could not get token for authentication, error code %s" % (response.status_code)
                sys.exit(9)


def main(argv):

        if len(argv) == 0:
                usage()

        try:
                opts,args = getopt.getopt(argv,"i:hw:",["amip=","help","wf"])
        except getopt.GetoptError as err:
                print str(err)
                sys.exit(2)
        else:
                for opt,arg in opts:
                        if opt in ("-h","--help"):
                                usage()
                        if opt in ("-i","--amip"):
                                amip = arg
                        if opt in ("-w","--wf"):
                                wf = arg

        try:
                amip
        except:
                print "Required paramter -i|--amip not passed"
                sys.exit(9)
        
        try:
               wf 
        except:
                print "Required paramter -w|--wf not passed"
                sys.exit(9)


        data  = getsvcinfo(amip,wf)
        
        for d in data:
                f = json.loads(d['userData'])
                channelName =  f['channelName']
                channelId   =  f['channelId']
                for g in d['status']['captureStatus']:
                        print channelName + "," + channelId + "," + d['status']['state'] + "," + g['captureEngine']

if __name__ == '__main__':
    main(sys.argv[1:])