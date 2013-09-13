import urllib2

def getRequester(api_key):
	def makeRequest(**kwargs):
		url = "http://api.flickr.com/services/rest/?"
		kwargs["api_key"] = api_key
		kwargs["format"] = "json"
		kwargs["nojsoncallback"] = "1"		
		for pair in kwargs.items(): url += "&%s=%s" % pair		
		return urllib2.urlopen(url).readlines()	
		
	return makeRequest
