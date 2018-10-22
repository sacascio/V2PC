#!/usr/bin/env python

import sys
import getopt
import re
import json
from IPy import IP
import requests
import os
import warnings

warnings.filterwarnings("ignore")



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


def getchannels(ip,token):     
    url = "https://%s:8443/api/platform/do/v2/channelsources" % (ip)
    headers = { 'Content-Type':'application/json', 'Authorization' : 'Bearer %s ' % token }
    response = requests.get(url,headers=headers, verify=False, timeout=30)
    
    if response.status_code == 200:
        return response.json()  
    
    else:
        print "Could not get channel list"
        sys.exit(9) 

def getstrprofiles(ip,token): 
    profvalues = {}
        
    url = "https://%s:8443/api/platform/do/v2/streamprofiles" % (ip)
    headers = { 'Content-Type':'application/json', 'Authorization' : 'Bearer %s ' % token }
    response = requests.get(url,headers=headers, verify=False, timeout=30)
    
    if response.status_code == 200:
        for d in response.json():
            abrname = d['properties']['publishName']
            abrid   = d['name']
            
            if abrname in profvalues:
                print "ERROR: ABR Profile names must be unique. Found multiple ABR Profiles named %s  Please correct names in V2PC" % pubname
                sys.exit(9)
            
            else:
                profvalues[abrname] = abrid
        
        return profvalues
    
    else:
        print "Could not get streaming profiles"
        sys.exit(9)       
        
def usage():

    print " The following parameters are required:\n\n \
    \
        f:      Name of input file ( ex. %s -f file.csv )\n \
        d:      Domain name (ex. -d mos.hcvlny.cv.net)\n \
        h:      Help message\n\n \
        Input file format ChannelDescription,Callsign,SourceIP,SD or HD,MulticastIP" % (sys.argv[0])

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
        

    try:
        ip
    except:
        print "Required paramter -i|--masterip not passed"
        sys.exit(9)
  
    
                                
    # Remove duplicates, if any
    #lines = list(set(lines))
                    
                    
    if opt == '-h':
        usage()
        
    token = gettoken(ip,username,password)
    #print json.dumps(getchannels(ip,token),indent=2)
    print getstrprofiles(ip,token)
    
    sys.exit(9)
    
if __name__ == '__main__':
    main(sys.argv[1:])
