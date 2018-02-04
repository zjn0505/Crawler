import webapp2, logging, urllib2
from datetime import datetime
from google.appengine.ext import ndb
from google.appengine.api import memcache

class DepartifyJson (ndb.Model):
    api = ndb.StringProperty()
    json = ndb.TextProperty()
    last_check_time = ndb.DateTimeProperty()

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        query = DepartifyJson.query()
        logging.info("Get Departify Styles")
        result = memcache.get('departify_styles')
        if result is not None:
            self.response.write(result)
        else:
            for entity in query:
                result = entity.json
                break
            memcache.add('departify_styles', result, 3600)
            self.response.write(result)
        print "end"

class Refresh(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        result = None
        query =DepartifyJson.query(DepartifyJson.api== 'styles')
        if query.count() == 0:
            result = DepartifyJson()
            result.last_check_time = datetime.now()
        else:
            for entity in query:
                result = entity
                break
        request = urllib2.Request("https://api.deeparteffects.com/v1/noauth/styles", headers={"x-api-key" : "n0oZQBDc73923UTkoTju827gUvY5YTjT8UQIDCXq"})
        result.json = urllib2.urlopen(request).read()
        result.last_check_time = datetime.now()
        result.api = "styles"
        result.put()
        memcache.add('departify_styles', result, 3600)
        self.response.write(result.json)
        print "end"

app = webapp2.WSGIApplication([
    ('/departify', MainPage),
    ('/departify/refresh', Refresh),
], debug=True)
