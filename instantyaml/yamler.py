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
    styles = [(None, 'Default'), ('"', 'Double quote - "'), ("'", "Single quote - '")]
    default_style = forms.ChoiceField(required=False, choices=styles)
    flow_styles = [(None, 'Default'), (False, 'New lines'), (True, "Same line (flow style)")]
    default_flow_style = forms.ChoiceField(required=False, choices=flow_styles)
    indents = [(1, '1'), (2, '2'), (4, '4'), (8, '8')]
    indent = forms.ChoiceField(choices=indents, initial='4')
    widths = [(20, '20'), (40, '40'), (60, '60'), (80, '80'), (100, '100'), (120, '120')]
    width = forms.ChoiceField(choices=widths)
    versions = [(0, '1.0'), (1, '1.1')]
    version = forms.ChoiceField(choices=versions, help_text="YAML version")
    events = forms.BooleanField()
    tokens = forms.BooleanField()
                                     
class MainPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            path = os.path.join(os.path.dirname(__file__), 'featured.html')
            form = FormatForm({'canonical': True, 'explicit_start': True, 'explicit_end': True,
                               'default_style': None, 'default_flow_style': None, 'indent': 4, 
                               'width': 80, 'version': 1, 'events': False, 'tokens': False})
            template_values = {"form": form, "logout_url": users.create_logout_url(self.request.uri)}
        else:
            path = os.path.join(os.path.dirname(__file__), 'welcome.html')
            template_values = {"login_url": users.create_login_url(self.request.uri)}
            
        self.response.out.write(template.render(path, template_values))
    
    def post(self):
        user = users.get_current_user()

        if user:
            path = os.path.join(os.path.dirname(__file__), 'featured.html')
            form = FormatForm({'canonical': True, 'explicit_start': True, 'explicit_end': True,
                               'default_style': None, 'default_flow_style': None, 'indent': 4, 
                               'width': 80, 'version': 1, 'events': False, 'tokens': False})
            template_values = {"form": form, "logout_url": users.create_logout_url(self.request.uri)}
        else:
            content = self.request.get('content')
            try:
                document = yaml.load(content)
                result = yaml.dump(document, default_style='"', default_flow_style=False,
                                   canonical=True, indent=4, width=80,
                                   explicit_start=True, explicit_end=True, version=(1, 1))
                """ 1 < indent < 10, width > 20"""
            except:
                result = "The document is not valid YAML:\n%s" % content
            path = os.path.join(os.path.dirname(__file__), 'welcome.html')
            template_values = {"result": result, "content": content}
        self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication(
                                      [('/', MainPage)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()