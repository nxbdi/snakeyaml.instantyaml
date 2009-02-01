from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
import os
import cgi
import yaml

"""
class Attempt(db.Model):
  author = db.UserProperty()
  content = db.StringProperty(multiline=True)
  date = db.DateTimeProperty(auto_now_add=True)
  valid = db.BooleanProperty()
"""
  
class MainPage(webapp.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'welcome.html')
    template_values = {}
    self.response.out.write(template.render(path, template_values))
    
class ValidatePage(webapp.RequestHandler):
  def post(self):
    content = self.request.get('content')
    try:
        document = yaml.load(content)
        result = yaml.dump(document, default_style='"', default_flow_style=False,
                           canonical=True, indent=4, width=80,
                           explicit_start=True, explicit_end=True)
    except:
        result = "The document is not valid YAML:\n%s" % content
    path = os.path.join(os.path.dirname(__file__), 'validate.html')
    template_values = {"validated": result}
    self.response.out.write(template.render(path, template_values))


application = webapp.WSGIApplication(
                                      [('/', MainPage),
                                      ('/validate', ValidatePage)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()