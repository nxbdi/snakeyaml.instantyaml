from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
import os
import cgi
import yaml
from yamler import Attempt

class Stat(object):
    def __init__(self, user, date):
        self.user = user
        self.counter = 1
        self.date = date
        
    def add(self, date):
        self.counter += 1
        self.date = date
        
    
class AdminPage(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'admin.html')
        attempts = {}
        counter = Attempt.all().count()
        for attempt in Attempt.all():
            author = attempt.author.email()
            if not author:
                author = "Anonymous@nowhere.com"
            if author not in attempts:
                stat = Stat(author, attempt.date)
                attempts[author] = stat
            else:
                stat = attempts[author]
                stat.add(attempt.date)
        statistics = attempts.values()
            
        template_values = {"counter": counter, "statistics": statistics}
        self.response.out.write(template.render(path, template_values))
        
application = webapp.WSGIApplication(
                                      [('/admin/', AdminPage)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()