#!/usr/bin/env python

import sys
import getopt
import re
import json
from IPy import IP
import requests
import os

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
    
    
    fileerr = False

    try:
        opts,args = getopt.getopt(argv,"f:d:p:u:",["file=","domain=","profile","udpports"])
    except getopt.GetoptError as err:
        print str(err)
        sys.exit(2)
    else:
        for opt,arg in opts:
            if opt in ("-d","--domain"):
                domain = arg
          
            if opt in ("-f", "--file"):
                file = arg
          
            if opt in ("-p", "--profile"):
                profile = arg
         
            if opt in ("-u", "--udpports"):
                udpports = arg
        
        
        try:
            domain
        except:
             sys.argv[0] + "Domain not specified (-d|--domain)"
             sys.exit(1) 
        
        try:
            profile
        except:
            print sys.argv[0] + "Streaming profile file not specified (-p|--profile)"
            sys.exit(1)
            
        try:
            file
        except:
            print sys.argv[0] + "Input file not specified (-f|--file)"
            sys.exit(1)
            
        try:
            udpports
        except:
            print sys.argv[0] + "UDP Ports file not specified (-u|--udpports)"
            sys.exit(1)
                           
        if not os.path.isfile(file):
            print sys.argv[0] + " Input file %s passed to -f|--file NOT found" % file
            sys.exit(1)
                    
        elif not os.path.isfile(profile):
            print sys.argv[0] + " Profile file %s passed to -p|--profile NOT found" % file
            sys.exit(1)
                
        elif not os.path.isfile(udpports):
            print sys.argv[0] + " UDP port file %s passed to -u|--udpports NOT found" % file
            sys.exit(1)    
                    
        else:
            # ChannelDescription,Callsign,SourceIP,SD or HD,MulticastIP
            with open (file) as data:
                lines = data.read().splitlines()
                        
            for data in lines:
                fieldnum = data.split(",")
                if len(fieldnum) != 5:
                    print ("Input file format does not have 5 fields.  %s configured. See line %s of input file") % (len(fieldnum),lines.index(data) + 1)
                    fileerr = True
                            
                try:
                    IP(fieldnum[2])
                except:
                    print ("Source IP address %s is not a valid IP address.  See line %s of input file" ) % (fieldnum[2],lines.index(data) + 1)
                    fileerr = True
                            
                try:
                    IP(fieldnum[4])
                except:
                    print ("Multicast IP address %s is not a valid IP address.  See line %s of input file" ) % (fieldnum[4],lines.index(data) + 1)
                    fileerr = True
                            
                if fieldnum[3].upper() != 'SD' and fieldnum[3].upper() != 'HD':
                    print ("SD or HD must be specified after the source IP.  %s specified.  See line %s of input file" ) % (fieldnum[3],lines.index(data) + 1)
                    fileerr = True
                                
            # Remove duplicates, if any
            lines = list(set(lines))
                    
                    
            if opt == '-h':
                usage()
    
if __name__ == '__main__':
    main(sys.argv[1:])
