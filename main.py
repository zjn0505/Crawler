import webapp2, logging
execfile("checkDate.py")
from google.appengine.ext import ndb

class MainPage(webapp2.RequestHandler):
    def get(self):
        logging.info("Enter MainPage")
        print_content(self)
        self.response.write('<a href="refresh">Check again</a>')
        print "end"

class Refresh(webapp2.RequestHandler):
    def get(self):
        getDate()
        print_content(self)
        print "end"

def print_content(self):
    self.response.write('<p>Checking the last update date of MSN Android apps</p>')
    query = App.query()
    date = datetime.now()
    for app in query:
        self.response.write('<p>%-*s last update on: %s</p>' % (11, app.friendly_name, app.last_update_time))
	date = app.last_check_time
    delta = datetime.now() - date
    d = divmod(delta.total_seconds(), 86400) # days
    h = divmod(d[1], 3600) # hours
    m = divmod(h[1],60)  # minutes
    s = m[1]  # seconds
    self.response.write('<p>This check was performed : %d days %d hours %d minutes %d seconds ago</p>' % (d[0],h[0],m[0],s))


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/refresh', Refresh),
], debug=True)
