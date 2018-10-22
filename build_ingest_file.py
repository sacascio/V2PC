#!/usr/bin/env python
import requests;
import sys
import warnings
import json

warnings.filterwarnings("ignore")

def getassets(ip,wf):
	a = []

	for n in range(100):
		n = n + 1
	
		url = "https://" + ip + ":7001/v1/assetworkflows/" + wf + "/assets?limit=500&page=" + str(n)
		headers = { 'Content-type':'application/json' }
		response = requests.get(url,headers=headers, verify=False, timeout=30)

		if response.status_code == 200:
			if len(response.json()) == 0:
				break

			else:
				if len(a) == 0:
					a = response.json()
				else:
					a = a + response.json()

		else:
			print "FAILED to get url %s, error code %s" % (url,response.status_code)
			sys.exit(9)
	return a
	
def getassetdetail(ip,wf,asset):

	url = "https://" + ip + ":7001/v1/assetworkflows/" + wf + "/assets/" + asset
	headers = { 'Content-type':'application/json' }
	response = requests.get(url,headers=headers, verify=False, timeout=30)

	if response.status_code == 200:
		return response.json()

	else:
		print "FAILED, error code %s" % response.status_code

def getProfiles(data):
	profiles = []

	for a in data['mediaSource']['streams']:
		s_name = a['name']
		s_name = s_name.strip()
	 	tmp = s_name.split('_')
		br = tmp[2]
		br = str(br)
		br = br.replace('kb','')
	
		if not br.isdigit():
			print "ERROR: " + br + " is not a valid number, asset name %s" % s_name
			sys.exit(9)
		else:
			profiles.append(br)

	profiles.sort(key=int)
	return profiles			

def main(argv):
	ip = '10.105.111.73'
	wf = 'dfwvodblu'
	f = open("contentList","w")

	allassets = getassets(ip,wf)

	for a in allassets:
		cid = a['contentId']
		data = {}
		d_profiles = {}
		assets = getassetdetail(ip,wf,cid)
		
		try:
			 assets['statusCallback']
		except:
			data['statusCallback'] = { "url": "http://1.1.1.1/CAB/assetnotf" } 
		else:
			data['statusCallback'] = assets['statusCallback']

		data['contentId'] =   assets['contentId']
		data['contentName'] = assets['contentId']
		data['mediaSource'] = {}
		data['mediaSource']['ebpMode']= assets['mediaSource']['ebpMode']
		data['mediaSource']['streams'] = {}

		for i in assets['mediaSource']['streams']:
			if len(data['mediaSource']['streams']) == 0:
				data['mediaSource']['streams'] = [ ({'name': i['name'], 'sourceUrl' : i['sourceUrl']}) ]
			else:
				data['mediaSource']['streams'].append({'name': i['name'], 'sourceUrl' : i['sourceUrl']})
		
		profiles = getProfiles(data)

		if len(profiles) < 6:
			print "SKIPPING %s, has %s profiles" %  ( cid,len(profiles) )
		else:
			d_profiles[profiles[0]] = 'audio32'	
			d_profiles[profiles[1]] = 'audio32'	
			d_profiles[profiles[2]] = 'audio96'	
			d_profiles[profiles[3]] = 'audio96'	
			d_profiles[profiles[4]] = 'audio96'	
			d_profiles[profiles[5]] = 'audio96'	
	
		for d in data['mediaSource']['streams']:
			s_name = d['name']
                	tmp = s_name.split('_')
                	br = tmp[2]
                	br = str(br)
                	br = br.replace('kb','')

			if br in d_profiles:
				d['audioGroup'] = []
                                d['audioGroup'] = d_profiles[br]	

		with open('../VODFiles/' + wf + '_' + data['contentId'] + '.json', 'w') as outfile:
			json.dump(data,outfile,indent=2)
		
		f.write(wf + '/' + cid + "\n")
	f.close
if __name__ == '__main__':
	main(sys.argv[1:])

