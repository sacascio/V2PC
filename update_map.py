#!/usr/bin/env python

import sys
import getopt
import re
import json
import os
import warnings


warnings.filterwarnings("ignore")

def update_map(mapfile,exclude_list):
        count = 0
        
        with open (exclude_list) as e:
            channels = e.read().splitlines()
        
        with open (mapfile) as chmapjson:
            channel_map = json.load(chmapjson)
         
        for index,d in enumerate(channel_map['properties']['sources']):
            if d['contentId'] in channels:
                count = count + 1
                print "Drop %s" % d['contentId']
                del channel_map['properties']['sources'][index]
                
        print "Dropped %s channels" % count
        
        with open('Hicksville.new', 'w') as outfile:
            json.dump(channel_map, outfile, indent=1)

def usage():

    print " \n\n         The following parameters are required:\n\n \
        m: Name of channel map file as defined in V2PC in JSON output \n \
        e: list of channels to drop (exclude list) \n \
        h: Help message\n\n \
        " 

    sys.exit(9)

def main(argv):
    
    if len(argv) == 0:
        usage()
        
   

    try:
        opts,args = getopt.getopt(argv,"m:e:h",["map=","exclude=","help"])
    except getopt.GetoptError as err:
        print str(err)
        sys.exit(2)
    else:
        for opt,arg in opts:
            if opt in ("-h","--help"):
                usage()
            if opt in ("-m","--map"):
                mapfile = arg
            if opt in ("-e","--exclude"):
                exclude_list = arg
        

    
    try:
        mapfile
    except:
        print "Required paramter -m|--map not passed"
        sys.exit(9)
        
    try:
        exclude_list
    except:
        print "Required paramter -e|--exclude name not passed"
        sys.exit(9)
    
    if opt == '-h':
        usage()
        
    
    update_map(mapfile,exclude_list)
    print "DONE"
    sys.exit(9)
    
if __name__ == '__main__':
    main(sys.argv[1:])

        