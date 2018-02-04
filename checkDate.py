import sys
sys.path.insert(0, 'lib')
from google.appengine.ext import ndb
from datetime import datetime

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

from bs4 import BeautifulSoup

class App(ndb.Model):
    packagename = ndb.StringProperty()
    friendly_name = ndb.StringProperty()
    last_update_time = ndb.StringProperty()
    last_check_time = ndb.DateTimeProperty()

BASE_URL = "https://play.google.com/store/apps/details?id=com.microsoft.amp.apps."

def checkdate(package):
    app = App.query(App.packagename == package).get()
    url = BASE_URL + package
    html = urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
    app.last_update_time = soup.find("div", {"class" : "content", "itemprop" : "datePublished"}).string
    app.last_check_time = datetime.now()
    app.put()

def getDate():
    init()
    query = App.query()
    for app in query:
        checkdate(app.packagename)

def init():
    query = App.query()
    if query.count() == 0:
        bingnews = App(packagename="bingnews", friendly_name="MSN News")
        bingsports = App(packagename="bingsports", friendly_name="MSN Sports")
        bingfinance = App(packagename="bingfinance", friendly_name="MSN Money")
        bingweather = App(packagename="bingweather", friendly_name="MSN Weather")
        bingnews.put()
        bingsports.put()
        bingfinance.put()
        bingweather.put()
