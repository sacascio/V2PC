#!/usr/bin/env python

import sys
import getopt
import json
import warnings


warnings.filterwarnings("ignore")


def create_lineup(filename,lineup):
    
    
    gdata = {}
    gdata.update({ 'id' : 'smtenant_0.smchannellineup.%s' % lineup} )
    gdata.update({ 'name' : lineup } )
    gdata.update({ 'type' : 'channellineups' } )
    gdata.update({ 'externalId' : '/v2/channellineups/%s' % lineup} )
    gdata['properties'] = {}
    gdata['properties']['description'] = ''
    gdata['properties']['mediaArchiveRef'] = ''
    gdata['properties']['sources'] = []

    with open (filename) as f:
        lines = f.read().splitlines()
        
    
    for tname in lines:
        (name,cid) = tname.split(",")
        
        data = {}
        data["sourceRef" ] = "smtenant_0.smchannelsource.%s" % name
        data["contentId" ] = cid
        data["customConfigs" ] = []
        data["customConfigs" ].append(
                        {
                            "name": "maxRetryCount",
                            "value": "-1"
                        }
                        )
          
    

    
        if len(gdata['properties']['sources']) > 0:
            gdata['properties']['sources'].append(data)
        else:
            gdata['properties']['sources'] = []
            gdata['properties']['sources'].append(data)
    
    
    return gdata

        
def usage():

    print " \n\n         The following parameters are required:\n\n \
        f: Name of input file - channel name and content ID comma seperated \n \
        h: Help message\n\n \
        l: Name of lineup to add channel to \n\n \
        Example: %s -f file.csv  -l hicksville\n\n \
        " % (sys.argv[0])

    sys.exit(9)


def main(argv):
    
    if len(argv) == 0:
        usage()
        
   

    try:
        opts,args = getopt.getopt(argv,"f:l:h",["file=","lineup=","help"])
    except getopt.GetoptError as err:
        print str(err)
        sys.exit(2)
    else:
        for opt,arg in opts:
            if opt in ("-h","--help"):
                usage()
            if opt in ("-f","--filename"):
                filename = arg
            if opt in ("-l","--lineup"):
                lineup = arg
        

    
    try:
        filename
    except:
        print "Required paramter -f|--filename not passed"
        sys.exit(9)
        
    try:
        lineup
    except:
        print "Required paramter -l|--lineup name not passed"
        sys.exit(9)
    
    if opt == '-h':
        usage()
        
    
    gdata = create_lineup(filename,lineup)
    print json.dumps(gdata,indent = 2)
    sys.exit(9)
    
if __name__ == '__main__':
    main(sys.argv[1:])
