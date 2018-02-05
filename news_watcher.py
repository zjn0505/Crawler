import webapp2 
from urllib import request, parse
import json, asyncio
from datetime import datetime
from aiohttp import ClientSession
regions_list = '["de-de","en-au","en-ca","en-gb","en-in","en-us","es-es","es-mx","fr-ca","fr-fr","it-it","ja-jp","nl-nl","pt-br","ru-ru","en-sa","es-xl","da-dk","el-gr","en-ph","es-cl","es-co","es-pe","es-ve","en-my","pt-pt","th-th","en-ae","de-at","de-ch","en-ie","en-nz","en-sg","en-za","es-ar","es-us","fi-fi","fr-be","fr-ch","id-id","ko-kr","nb-no","nl-be","pl-pl","sv-se","tr-tr","vi-vn","zh-hk","zh-tw"]'
regions_list_test = '["de-de","en-au"]'
template = "https://cdn.content.prod.cms.msn.com/common/abstract/alias/experiencebyname/today?count=20&market=%s&tenant=amp&vertical=news"
regions = json.loads(regions_list)
serverChanTemplate = "https://pushbear.ftqq.com/sub?sendkey=2416-5a670a3a79051d6495cbb17758b361b9&text=%s Potential Errors %d&desp=Error Msg: %s\n\nFull report https://pullsh.me/%s"

report = ""
error = 0
errorMsg = ""

def extractHeadlineNode(document, headlines_href):
	for node in document:
		if node["_links"]["self"][0]["href"] == headlines_href:
			return node

def extractHeadlineName(data, headlines_href):
	modules = data["canvases"][0]["regions"][0]["modules"]
	for module in modules:
		if len(module.get("sources", "")) == 0:
			continue
		if module["sources"][0].get("href", "") == headlines_href:
			# print module
			return module["name"]
def task():
	global report
	report = ""
	global error
	error = 0
	result = ""
	global errorMsg
	errorMsg = ""
	loop = asyncio.get_event_loop()
	future = asyncio.ensure_future(loopAll(loop))
	loop.run_until_complete(future)

async def loopAll(loop):
	tasks = []
	for region in regions:
		task = parseOneRegionAsync(region)
		tasks.append(task)
	responses = await asyncio.gather(*tasks)
	
	print(responses)
	msg = ""
	for response in responses:
		msg += (response +"\n\n") 
	url = 'https://api.jienan.xyz/memo'
	data = parse.urlencode({'msg' : msg}).encode()
	req = request.Request(url, data=data)
	resp = request.urlopen(req)
	memo = json.loads(resp.read())
	id = memo["memo"]["_id"]
	
	url = serverChanTemplate % (str(datetime.now().isoformat()), error, errorMsg, id)
	
	print(url + "")
	print(parse.quote(url, safe=':/=?&'))
	request.urlopen(parse.quote(url, safe=':/=?&')).read()
	
	
def taskTest():
	global report
	report = ""
	global error
	error = 0
	global errorMsg
	errorMsg = ""
	loop = asyncio.get_event_loop()
	future = asyncio.Future()
	asyncio.ensure_future(parseOneRegionAsync("zh-hk"))
	loop.run_until_complete(future)
	report += future.result() + "\n\n"
	print(report)
	url = serverChanTemplate % (str(datetime.now().isoformat()), error, report)
	print(url + "")
	print(parse.quote(url, safe=':/=?&'))
	request.urlopen(parse.quote(url, safe=':/=?&')).read()

async def parseOneRegionAsync(region):
	print(region)
	global error
	result = "";
	global errorMsg
	errorMsg = ""
	result += "== Start to crawl " + region +"==\n\n"
	url = template % region
	print(url)
	async with ClientSession() as session:
		async with session.get(url) as response:
			response = await response.read()
			data = json.loads(response)
			document = data["_embedded"]["documents"]
			refs = data["_links"]["references"]
			for ref in refs:
				if ref.get("type", "") != "list":
					continue
				href = ref["href"]
				ref_node = extractHeadlineNode(document, href)
				ref_name = extractHeadlineName(data, href)
				try:
					ref_articles = len(ref_node["_links"]["references"])
				except KeyError:
					error += 1
					errorMsg += ("%s has an invalid node with id %s\n" % (region, href))
				print("%s with id %s has article count %d" % (ref_name, href, ref_articles))
				if ref_articles == 0:
					error += 1
					errorMsg += ("%s has an invalid node with id %s\n" % (region, href))
				result += " %s has article count %d\n\n" % (ref_name, ref_articles)
			return result

def parseOneRegion(region):
	print(region)
	global error
	global errorMsg
	errorMsg = ""
	result = "";
	result += "== Start to crawl " + region +"==\n\n"
	response = request.urlopen(template % region)
	data = json.load(response)
	document = data["_embedded"]["documents"]
	refs = data["_links"]["references"]
	for ref in refs:
		if ref.get("type", "") != "list":
			continue
		href = ref["href"]
		# print(href)
		ref_node = extractHeadlineNode(document, href)
		ref_name = extractHeadlineName(data, href)
		# print(ref_name)
		try:
			ref_articles = len(ref_node["_links"]["references"])
		except KeyError:
			error += 1
			errorMsg += ("%s has an invalid node with id %s\n" % (region, href))
		print("%s with id %s has article count %d" % (ref_name, href, ref_articles))
		if ref_articles == 0:
			error += 1
			errorMsg += ("%s has an invalid node with id %s\n" % (region, href))
		result += " %s article %d\n\n" % (ref_name, ref_articles)
	return result
	
task()
	
class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write(task())
        print("end")
		
		
app = webapp2.WSGIApplication([
    ('/', MainPage)
], debug=True)
