#!/usr/bin/env python

# script to split channel map into X number of maps evenly based on channel profile

import sys
import re
import json
import os
import warnings


warnings.filterwarnings("ignore")

def addtolineup(addtomap,channel,cid,maps):
    
    maps[addtomap]['properties']['sources'].append({'sourceRef' : 'smtenant_0.smchannelsource.%s' % channel, 'contentId' : cid, 'customConfigs' : [{'value': -1, 'name' : 'maxRetryCount'}]})
    return maps
    #print json.dumps(maps[addtomap])
    #sys.exit(9)
                                                  
                                                  

def getsdhdmap (channelsources):
    finalcnt = {}
    with open (channelsources) as f:
        data = json.load(f)
    
    for d in data:
        numprofiles =  len(d['properties']['streams'])
        finalcnt.update({d['name'] : numprofiles})
        
    return finalcnt
            

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
      
    nummaps = 5  
    mapnames = "map"
    
    hdnextmap = 1
    sdnextmap = 1
    mcnextmap = 1
    
    sdhd = getsdhdmap('channelsources')
    
    maps = initialize_maps(nummaps, mapnames)
    
    for d in sdhd:
        if hdnextmap == nummaps+1:
            hdnextmap = 1
        
        if sdnextmap == nummaps+1:
            sdnextmap = 1   
            
        if mcnextmap == nummaps+1:
            mcnextmap = 1   
        
        if sdhd[d] == 1:
            addtomap = mapnames + str(mcnextmap)
            mcnextmap = mcnextmap + 1
            
        if sdhd[d] == 4:
            addtomap = mapnames + str(sdnextmap)
            sdnextmap = sdnextmap + 1
            
        if sdhd[d] == 6:
            addtomap = mapnames + str(hdnextmap)
            hdnextmap = hdnextmap + 1
        
        cid = d
        cid  = cid.replace("-","_")
        maps = addtolineup(addtomap,d,cid,maps)
    
    print json.dumps(maps)
    
if __name__ == '__main__':
    main(sys.argv[1:])
