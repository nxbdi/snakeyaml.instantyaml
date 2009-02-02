from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
import os
import cgi
import yaml
from yamler import Attempt

class AdminPage(webapp.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), 'admin.html')
        counter = Attempt.all().count()
        template_values = {"counter": counter, "attempts": Attempt.all()}
        self.response.out.write(template.render(path, template_values))
        
application = webapp.WSGIApplication(
                                      [('/admin/', AdminPage)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()