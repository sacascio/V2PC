#!/usr/bin/env python

import sys
import getopt
import re
import json
from IPy import IP
import requests
import os
import warnings
from IPy import IP

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
    clist = []
    url = "https://%s:8443/api/platform/do/v2/channelsources" % (ip)
    headers = { 'Content-Type':'application/json', 'Authorization' : 'Bearer %s ' % token }
    response = requests.get(url,headers=headers, verify=False, timeout=30)
    
    if response.status_code == 200:
        for d in response.json():
            clist.append(d['name'])
            clist.append(d['properties']['channelId'])
            
        return clist

    else:
        print "Could not get channel list"
        sys.exit(9) 


def checkvalidIP(ip,index,addrtype):
    try:
        IP(ip)
    except:
        print "Invalid %s IP address on line %s (%s)" % (addrtype,index,ip)
        sys.exit(9)
        
def loadfile(filename):
    rdata = {}
    
    with open (filename) as f:
        lines = f.readlines()
        
        # Remove duplicates
        lines = list(set(lines))
        
        for idx,l in enumerate(lines):
            idx = idx  + 1
            l = l.strip()
            tmp = l.split(',') 
            
            if len(tmp) != 8:
                print "Missing data in line %s of input file.  Please recheck input file" % idx
                sys.exit(9)
            
            if tmp[0] == '' :
                print "Missing service name in input file, line %s" % idx
            
            if len(tmp[0]) > 63:
                print "Service name %s is too long, maximum is 63 characters, %s provided" % (tmp[0],len(tmp[0]))
                
            for t in tmp[0]:
                if not t.isalnum() and t != '_' and t != '-':
                    print "Service %s can only contain alphanumeric characters. Please remove '%s' character" % (tmp[0],t)
                    sys.exit(9)
            
            if tmp[1] != '' :
                checkvalidIP(tmp[1],idx,"Source")
                sip1 = tmp[1]
            else:
                sip1 = ''
                
            if tmp[2] == '' :
                print "Missing Primary Multicast Address in input file, line %s" % idx
            else:
                 checkvalidIP(tmp[2],idx,"Multicast")
                
            if tmp[3] == '' :
                print "Missing UDP Port in input file, line %s" % idx
            else:
                if not int(tmp[3].isdigit()) or int(tmp[3]) < 1024 or int(tmp[3]) > 65535:
                    print "UDP Port %s is not valid on line %s" % (tmp[3],idx)
                    sys.exit(9)
                
            if tmp[4] != '' :
                checkvalidIP(tmp[4],idx,"Source")
                sip2 = tmp[4]
            else:
                sip2 = ''
                
            if tmp[5] != '' :
                checkvalidIP(tmp[5],idx,"Multicast")
            
            if tmp[6] != '':
                if not int(tmp[6].isdigit()) or int(tmp[6]) < 1024 or int(tmp[6]) > 65535:
                    print "UDP Port %s is not valid on line %s" % (tmp[6],idx)
                    sys.exit(9)
            
            if tmp[5] != '' and tmp[6] != '':
                surl2 = "udp://%s:%s" % ( tmp[5],tmp[6])
                
            else:
                surl2 = ''
               
                if tmp[0] in rdata:
                    rdata[tmp[0]].append({
                                      'pubname' : tmp[7],  
                                      'sip1'    : sip1,
                                      'surl1'   : 'udp://%s:%s' % (tmp[2],tmp[3]),
                                      'sip2'    : sip2,
                                      'surl2'   : surl2
                                    })
                else:
                    rdata[tmp[0]] = {}
                
                    rdata[tmp[0]] = [ {
                                      'pubname' : tmp[7],  
                                      'sip1'    : sip1,
                                      'surl1'   : 'udp://%s:%s' % (tmp[2],tmp[3]),
                                      'sip2'    : sip2,
                                      'surl2'   : surl2

                                      }]
                    
            
         
    return rdata
    
def addchannels(ip,token,strprofiles,idata,currchannels,lineup,add2lineup,channelsinlug):    
   
    headers = { 'Content-Type':'application/json', 'Authorization' : 'Bearer %s ' % token }
    
    for name in idata:
        if name in currchannels:
            print "WARNING: Channel %s already exists in V2PC.  Skipping" % name
            continue
        
        data = {}
        data['properties'] = {}
        data['properties']['streams'] = {}
        data['name'] = name
        data['externalId'] = "/v2/channelsources/%s" % name
        data['type'] = "channelsources"
        data['id'] = "smtenant_0.smchannelsource.%s" % name
        data['properties']['maxAudioStreams'] = "10"
        data['properties']['nodedupe'] = "false"
        data['properties']['channelId'] = name
        data['properties']['streamType'] = 'ATS'
        data['properties']['iframeSegmentDurationInSec'] = ''
        
       
        for streams in idata[name]:
            if len(data['properties']['streams']) == 0:
                data['properties']['streams'] = [ {
                                                   'publishSmptett' : True, 
                                                   'publishIframes' : True,
                                                   'publishName'    : streams['pubname'],
                                                   'profileRef'     : "smtenant_0.smstreamprofile.%s" % strprofiles[streams['pubname']],
                                                        'sources' : [ 
                                                                 {   
                                                                  'sourceIpAddr' : streams['sip1'],
                                                                  'sourceUrl'    : streams['surl1']
                                                                 },
                                                                {
                                                                 'sourceIpAddr' : streams['sip2'],
                                                                 'sourceUrl'    : streams['surl2']
                                                             
                                                                }]
                                                } ]
           
            else:
                data['properties']['streams'].append(  {
                                                   'publishSmptett' : True, 
                                                   'publishIframes' : True,
                                                   'publishName'    : streams['pubname'],
                                                   'profileRef'     : "smtenant_0.smstreamprofile.%s" % strprofiles[streams['pubname']],
                                                        'sources' : [ 
                                                                 {   
                                                                  'sourceIpAddr' : streams['sip1'],
                                                                  'sourceUrl'    : streams['surl1']
                                                                 },
                                                                {
                                                                 'sourceIpAddr' : streams['sip2'],
                                                                 'sourceUrl'    : streams['surl2']
                                                             
                                                                }]
                                                } )


        url = "https://%s:8443/api/platform/do/v2/channelsources/%s" % (ip,name)
        response = requests.post(url,headers=headers, data=json.dumps(data),verify=False, timeout=30)
        if response.status_code == 200:
            print "OK: Service %s added to V2PC" % name  
            
            if add2lineup is True:
                if name not in channelsinlug:
                    addchanneltolineup(ip,token,name,lineup)
                else:
                    print "Channel %s already in line up %s" % lineup
            
    
        else:
             print "ERROR: %s" % response.json()['error']

def addchanneltolineup(ip,token,name,lineup):
    headers = { 'Content-Type':'application/json', 'Authorization' : 'Bearer %s ' % token }
    url = "https://%s:8443/api/platform/do/v2/channellineups/%s" % (ip,lineup)
    data = {}
    
    data["sourceRef" ] = "smtenant_0.smchannelsource.%s" % name
    data["contentId" ] = name
    data["customConfigs" ] = []
    data["customConfigs" ].append(
                            {
                              "name": "maxRetryCount",
                              "value": "-1"
                            }
                           )
          
    response = requests.get(url,headers=headers,verify=False, timeout=30)
    gdata = response.json()
    
    if len(gdata['properties']['sources']) > 0:
        gdata['properties']['sources'].append(data)
    else:
        gdata['properties']['sources'] = []
        gdata['properties']['sources'].append(data)
    
    response = requests.put(url,headers=headers, data=json.dumps(data),verify=False, timeout=30)
    
    if response.status_code == 200:
            print "OK: Service %s added to lineup %s" % (name,lineup)
    else:
            print "ERROR: Could not add service %s to lineup %s"  % (name,lineup)
    
    
def validate_strprofiles(strprofiles,idata):
    for svc in idata:
        for str in idata[svc]:
            if str['pubname'] not in strprofiles:
                print "Streaming profile name %s is not defined in V2PC.  Please correct input file or V2PC" % str['pubname']
                sys.exit(9)

def validate_lineup(ip,token,lineup):
    svcs = []
    url = "https://%s:8443/api/platform/do/v2/channellineups/%s" % (ip,lineup)
    headers = { 'Content-Type':'application/json', 'Authorization' : 'Bearer %s ' % token }
    response = requests.get(url,headers=headers, verify=False, timeout=30)
    
    if response.status_code != 200:
        print "Channel lineup %s not found in V2PC.  Please create it first." % lineup
        sys.exit(9)
    else:
        for d in response.json()['properties']['sources']:
            svcs.append(d['contentId'])
    
        return svcs
    
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

    print " \n\nThe following parameters are required:\n\n \
        f: Name of input file \n \
        i: V2PC Master IP \n \
        h: Help message\n\n \
        Example: %s -f file.csv -i 10.8.3.25\n\n \
        Input file format: \n \
        ChannelName,SourceIP1,MulticastIP1,UDPPort1,SourceIP2,MulticastIP2,UDPPort2,StreamingProfileName \n\n \
        Optional Parameters: \n \
        SourceIP1,SourceIP2,MulticastIP2,UDPPort2 \n\n \
        Required: \n \
        ChannelName,MulticastIP1,UDPPort1,StreamingProfileName \n\n \
        ex: TEST6,13.159.0.22,239.192.1.6,5500,,,,725k\n\n" % (sys.argv[0])

    sys.exit(9)


def main(argv):
    
    if len(argv) == 0:
        usage()
        
    username = "admin"
    password = "default"
  

    try:
        opts,args = getopt.getopt(argv,"i:f:l:h",["masterip=","file=","lineup=","help"])
    except getopt.GetoptError as err:
        print str(err)
        sys.exit(2)
    else:
        for opt,arg in opts:
            if opt in ("-h","--help"):
                usage()
            if opt in ("-i","--masterip"):
                ip = arg
            if opt in ("-f","--filename"):
                filename = arg
            if opt in ("-l","--lineup"):
                lineup = arg
        

    try:
        ip
    except:
        print "Required paramter -i|--masterip not passed"
        sys.exit(9)
  
    try:
        filename
    except:
        print "Required paramter -f|--filename not passed"
        sys.exit(9)
        
    try:
        lineup
    except:
        add2lineup = False
    else:
        add2lineup = True
                    
    if opt == '-h':
        usage()
        
    token = gettoken(ip,username,password)
    
    if add2lineup is True:
        channelsinlug = validate_lineup(ip,token,lineup)
    else:
        lineup = ''
        channelsinlug = []
        
    currchannels = (getchannels(ip,token))
    strprofiles = getstrprofiles(ip,token)
    idata = loadfile(filename)
    validate_strprofiles(strprofiles,idata)
    addchannels(ip,token,strprofiles,idata,currchannels,lineup,add2lineup,channelsinlug)
    print "DONE"
    sys.exit(9)
    
if __name__ == '__main__':
    main(sys.argv[1:])
