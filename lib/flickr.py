import urllib2
import json

API_KEY = ""
GROUP_ID = "61141209@N05"

def getRequester(api_key):
	def makeRequest(**kwargs):
		url = "http://api.flickr.com/services/rest/?"
		kwargs["api_key"] = api_key
		kwargs["format"] = "json"
		kwargs["nojsoncallback"] = "1"		
		for pair in kwargs.items(): url += "&%s=%s" % pair		
		return json.loads(urllib2.urlopen(url).readlines())
		
	return makeRequest
	
def imageUrl(_info):#http://farm{farm-id}.staticflickr.com/{server-id}/{id}_{secret}.jpg
	info = _info["photo"]
	t = (info["farm"], info["server"], info["id"], info["secret"])
	return "http://farm%s.staticflickr.com/%s/%s_%s.jpg" % t
	


	
