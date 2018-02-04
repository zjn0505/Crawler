import sys, time
sys.path.insert(0, 'lib')
try:
        from urllib.request import urlopen
except ImportError:
        from urllib2 import urlopen
from bs4 import BeautifulSoup
from threading import Timer

BASE_URL = "https://play.google.com/store/apps/details?id=com.microsoft.amp.apps."
def checkdate(url):
        html = urlopen(url).read()
        soup = BeautifulSoup(html, 'html.parser')
        return (soup.find("div", {"class" : "content", "itemprop" : "datePublished"}).string + "\n" + soup.find("div", {"class" : "id-app-title"}).string)
def getDate():
        return ("MSN News last updated on "  + checkdate(BASE_URL + "bingnews") + "\n"
                "MSN Sports last updated on "  + checkdate(BASE_URL + "bingsports") + "\n"
                "MSN Money last updated on "  + checkdate(BASE_URL + "bingfinance") + "\n"
                "MSN Weather last updated on "  + checkdate(BASE_URL + "bingweather"))

def dailyTask():
	print "Upadating on" + time.ctime()
	print getDate()
	Timer(30, dailyTask).start()

dailyTask()
