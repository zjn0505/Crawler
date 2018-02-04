import sys, time
sys.path.insert(0, 'lib')
try:
        from urllib.request import urlopen
except ImportError:
        from urllib2 import urlopen
from bs4 import BeautifulSoup
from threading import Timer
from google.appengine.ext import ndb

BASE_URL = "https://play.google.com/store/apps/details?id="
DEFAULT_WATCHER = "msn_watcher"

class App(ndb.Model):
	packageName = ndb.StringProperty(required=True)
	name = ndb.StringProperty()
	releaseDate = ndb.StringProperty()
	lastCheck = ndb.DateTimeProperty(auto_now_add=True)
	subscriber = ndb.StringProperty(repeated=True)

def watcher_key(watcher_name=DEFAULT_WATCHER):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('app_watcher', watcher_name)

def initApp(package_name):
	app = App(parent=watcher_key(),
		packageName=package_name)
	app.key = ndb.key("App", package_name)
	app.put()



def checkdate(app):
    url = BASE_URL + app.package_name
    html = urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
    app.releaseDate = soup.find("div", {"class" : "content", "itemprop" : "datePublished"}).string
    app.name = soup.find("div", {"class" : "id-app-title"}).string
    app.put()

def getDate():
    app_query = App.query(
            ancestor=watcher_key(DEFAULT_WATCHER))
    apps = app_query.fetch()
    for app in apps:
    	checkdate(app)

def dailyTask():
    getDate()
    Timer(30, dailyTask).start()

def initAll():
	initApp("com.microsoft.amp.apps.bingnews")
	initApp("com.microsoft.amp.apps.bingsports")
	initApp("com.microsoft.amp.apps.bingfinance")
	initApp("com.microsoft.amp.apps.bingweather")

def getInfo():
    app_query = App.query(
            ancestor=watcher_key(DEFAULT_WATCHER))
    apps = app_query.fetch()
    result = ""
    for app in apps:
    	print "last check " + app.lastCheck
    	result = result + app.name + " last released on " + app.releaseDate + "\n"
    return result    

def query():
	Timer(100, getInfo).start()

# initAll()
# dailyTask()

# query()


