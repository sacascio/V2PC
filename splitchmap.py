#!/usr/bin/env python

# script to split channel map into X number of maps evenly based on channel profile

import sys
import json
import getopt
import warnings


warnings.filterwarnings("ignore")

def getmapstats(mapname,data,sdhd):
    profilecnt = 0
    sdcnt = 0
    hdcnt = 0
    mccnt = 0
    channelcount = len(data[mapname]['properties']['sources'])
    for x in data[mapname]['properties']['sources']:
        channelname =  x['sourceRef']
        channelname = channelname.replace('smtenant_0.smchannelsource.','')
        if sdhd[channelname] == 4:
            sdcnt = sdcnt + 1
        if sdhd[channelname] == 6:
            hdcnt = hdcnt + 1
        if sdhd[channelname] == 1:
            mccnt = mccnt + 1
        if sdhd[channelname] != 1 and sdhd[channelname] != 6 and sdhd[channelname] != 4:
            print channelname + ", %s profiles" % sdhd[channelname]
        profilecnt = profilecnt + sdhd[channelname]
    
    return channelcount,profilecnt,sdcnt,hdcnt,mccnt

def addtolineup(addtomap,channel,cid,maps):
    
    maps[addtomap]['properties']['sources'].append({'sourceRef' : 'smtenant_0.smchannelsource.%s' % channel, 'contentId' : cid, 'customConfigs' : [{'value': "-1", 'name' : 'maxRetryCount'}]})
    return maps
    
                                                  
                                                  

def getsdhdmap (channelsources):
    finalcnt = {}
    with open (channelsources) as f:
        data = json.load(f)
        
    
    for d in data:
        if ('sysMeta' in d  and len (d['sysMeta']['referringInstances']) == 0 ) or 'sysMeta' not in d:
            print "CHANNEL  %s is not in the lineup - SKIPPING" % d['name']
        else:
            numprofiles =  len(d['properties']['streams'])
            if numprofiles not in [1,4,6]:
                print "SKIPPING %s, num profiles is %s" %(d['name'], numprofiles)
            else:
                finalcnt.update({d['name'] : numprofiles})
        
        
    return finalcnt
            
def usage():
    
    print " \n\n         The following parameters are required:\n\n \
        n: Number of channel maps to create.  Must be a digit from 2 to 6 inclusive \n \
        h: Help message\n \
        m: Name of map - Map name will have the numbers 1,2,3 etc appended\n\n \
        Original channel map name (Hicksville) and original channel sources (channelsources) files are \n hardcoded into this script and assumed to be present in the same directory as this script\n\n"

    sys.exit(9)

def initialize_maps(numworkflows,mapname): 
    data = {}
    for i in xrange(1,numworkflows+1):
        origmapname = mapname
        origmapname = mapname + str(i)
        
        data[origmapname] = {}
        data[origmapname].update({ 'id' : 'smtenant_0.smchannellineup.%s' % origmapname} )
        data[origmapname].update({ 'name' : origmapname } )
        data[origmapname].update({ 'type' : 'channellineups' } )
        data[origmapname].update({ 'externalId' : '/v2/channellineups/%s' % origmapname} )
        data[origmapname]['properties'] = {}
        data[origmapname]['properties']['description'] = ''
        data[origmapname]['properties']['mediaArchiveRef'] = ''
        data[origmapname]['properties']['sources'] = []
        
    return data
        
def main(argv):
    
    if len(argv) == 0:
        usage()
        sys.exit(9)
    
    try:
        opts,args = getopt.getopt(argv,"n:hm:",["num=","help", "map"])
    except getopt.GetoptError as err:
        print str(err)
        sys.exit(2)
    else:
        for opt,arg in opts:
            if opt in ("-h","--help"):
                usage()
                sys.exit(9)
            if opt in ("-n","--num"):
                nummaps = arg
                if not nummaps.isdigit() or int(nummaps) < 1 or int(nummaps) > 6:
                    print "Number of workflows must be numeric and between 2 and 6"
                    sys.exit(9)
                else:
                    nummaps = int(nummaps)
                    
            if opt in ("-m","--map"):  
                mapnames = arg      
  
    try:
        mapnames
    except:
        print "Map name is not defined.  Define map name with -m option"
        sys.exit(9)
        
    try:
        nummaps
    except:
        print "Numer of maps is not defined.  Number of maps must be between 2 and 6"
        sys.exit(9)
        
    hdnextmap = 1
    sdnextmap = 1
    mcnextmap = 1
    
    sdhd = getsdhdmap('channelsources')
    
    maps = initialize_maps(nummaps, mapnames)
    
    for d in sdhd:
        #if hdnextmap == nummaps+1:
        #    hdnextmap = 1
        
        #if sdnextmap == nummaps+1:
        #    sdnextmap = 1   
            
        #if mcnextmap == nummaps+1:
        #    mcnextmap = 1   
        
        #if sdhd[d] == 1:
        #    addtomap = mapnames + str(mcnextmap)
        #    mcnextmap = mcnextmap + 1
            
        #if sdhd[d] == 4:
        #    addtomap = mapnames + str(sdnextmap)
        #    sdnextmap = sdnextmap + 1
            
        #if sdhd[d] == 6:
        #    addtomap = mapnames + str(hdnextmap)
        #    hdnextmap = hdnextmap + 1
        
        cid = d
        cid  = cid.replace("-","_")
        firstchar = cid[0]
        
        if firstchar.isdigit():
            addtomap = mapnames + str('1')

        else:
            firstchar = cid[0].upper()

            if firstchar >= 'A' and firstchar <= 'C':
                addtomap = mapnames + str('1')

            if firstchar >= 'D' and firstchar <= 'G':
                addtomap = mapnames + str('2')

            if firstchar >= 'H' and firstchar <= 'M':
                addtomap = mapnames + str('3')

            if firstchar >= 'N' and firstchar <= 'R':
                addtomap = mapnames + str('4')

            if firstchar == 'S':
                addtomap = mapnames + str('5')

            if firstchar >= 'T' and firstchar <= 'Z':
                addtomap = mapnames + str('6')
            
            maps = addtolineup(addtomap,d,cid,maps)
    
    for x in xrange(1,nummaps+1):
        #channelcnt,sd,hd,profilecnt = getmapstats(mapnames + str(x),maps)
        channelcnt,profilecnt,sdcnt,hdcnt,mccnt = getmapstats(mapnames + str(x),maps,sdhd)
        print "NUM CH: " + str(channelcnt) + ", NUM PROFILES: " + str(profilecnt) + ", NUM SD CH: " +  str(sdcnt) + ", NUM HD CH:" +  str(hdcnt) + ", NUM MC CH: " +  str(mccnt) + ", MAP NAME: " + mapnames + str(x) 
        
        f = open(mapnames + str(x), "w")
        f.write(json.dumps(maps[mapnames + str(x)], indent = 2)) 
        f.close()   
    #print json.dumps(maps)
    
if __name__ == '__main__':
    main(sys.argv[1:])
