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
        opts,args = getopt.getopt(argv,"f:d:",["file=","domain="])
    except getopt.GetoptError as err:
        print str(err)
        sys.exit(2)
    else:
        for opt,arg in opts:
            if opt in ("-d","--domain"):
                domain = arg
            if opt in ("-f", "--file"):
                file = arg
            
                if not os.path.isfile(file):
                    print sys.argv[0] + " Input file %s passed to -f|--file NOT found" % file
                    sys.exit(1)
                else:
                    # Verify file is in the following format: DISTRICT,DC,N7K-[A|B|C|D|E|F],IP
                    with open (file) as data:
                        lines = data.read().splitlines()
                        
                    for data in lines:
                        fieldnum = data.split(",")
                        if len(fieldnum) != 6:
                            print ("Input file format does not have 5 fields.  %s configured. See line %s of input file") % (len(fieldnum),lines.index(data) + 1)
                            fileerr = True
                            
                        try:
                            IP(fieldnum[2])
                        
                        except:
                            print ("Source IP address %s is not a valid IP address.  See line %s of input file" ) % (fieldnum[2],lines.index(data) + 1)
                     
                     # Remove duplicates, if any
                    lines = list(set(lines))
                    print lines
                    
                    
            if opt == '-h':
                usage()
    
if __name__ == '__main__':
    main(sys.argv[1:])
