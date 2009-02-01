from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import users
import os
import cgi
import yaml
from django import newforms as forms

"""
class Attempt(db.Model):
  author = db.UserProperty()
  content = db.StringProperty(multiline=True)
  date = db.DateTimeProperty(auto_now_add=True)
  valid = db.BooleanProperty()
"""
class FormatForm(forms.Form):
    canonical = forms.BooleanField()
    explicit_start = forms.BooleanField()
    explicit_end = forms.BooleanField()
                                     
class MainPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            path = os.path.join(os.path.dirname(__file__), 'featured.html')
            form = FormatForm({'canonical': True, 'explicit_start': True, 'explicit_end': True})
            template_values = {"form": form, "logout_url": users.create_logout_url(self.request.uri)}
        else:
            path = os.path.join(os.path.dirname(__file__), 'welcome.html')
            form = FormatForm({'canonical': True, 'explicit_start': True, 'explicit_end': True})
            template_values = {"login_url": users.create_login_url(self.request.uri)}
            
        self.response.out.write(template.render(path, template_values))
    
class ValidatePage(webapp.RequestHandler):
  def post(self):
    content = self.request.get('content')
    try:
        document = yaml.load(content)
        result = yaml.dump(document, default_style='"', default_flow_style=False,
                           canonical=True, indent=4, width=80,
                           explicit_start=True, explicit_end=True, version=(1, 1))
        """ 1 < indent < 10, width > 20"""
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