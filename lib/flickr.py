import urllib2
import json

API_KEY = ""
GROUP_ID = "61141209%40N05"

def getRequester(api_key):
	def makeRequest(**kwargs):
		url = "http://api.flickr.com/services/rest/?"
		kwargs["api_key"] = api_key
		kwargs["format"] = "json"
		kwargs["nojsoncallback"] = "1"		
		for pair in kwargs.items(): url += "&%s=%s" % pair		
		try:
			info = json.loads(urllib2.urlopen(url).readlines()[0])
			if info["stat"] == "ok": return info
		except:
			pass
		
	return makeRequest
	
def imageUrl(farm, server, pid, secret):	
	t = (farm, server, pid, secret)
	return "http://farm%s.staticflickr.com/%s/%s_%s.jpg" % t
	


	
