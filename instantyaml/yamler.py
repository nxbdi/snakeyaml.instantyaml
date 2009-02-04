from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
import os
import cgi
import latestyaml as yaml
from django import newforms as forms

class Attempt(db.Model):
  author = db.UserProperty(required=False)
  date = db.DateTimeProperty(auto_now_add=True)
  valid = db.BooleanProperty()
  content = db.TextProperty()
  
class FormatForm(forms.Form):
    canonical = forms.BooleanField(required=False)
    explicit_start = forms.BooleanField(required=False)
    explicit_end = forms.BooleanField(required=False)
    styles = [(0, 'Default'), ('"', 'Double quote - "'), ("'", "Single quote - '")]
    default_style = forms.ChoiceField(choices=styles)
    flow_styles = [(1, 'Default (block style if has nested collections)'), (2, 'Block style'), (3, "Flow style")]
    default_flow_style = forms.ChoiceField(choices=flow_styles)
    indents = [(1, '1'), (2, '2'), (4, '4'), (8, '8')]
    indent = forms.ChoiceField(choices=indents, initial='4')
    widths = [(20, '20'), (40, '40'), (60, '60'), (80, '80'), (100, '100'), (120, '120')]
    width = forms.ChoiceField(choices=widths)
    versions = [(0, '1.0'), (1, '1.1')]
    yaml_version = forms.ChoiceField(choices=versions)
    show_version = forms.BooleanField(required=False)
    show_events = forms.BooleanField(required=False)
    show_tokens = forms.BooleanField(required=False)
    show_node = forms.BooleanField(required=False)
                                     
class MainPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            path = os.path.join(os.path.dirname(__file__), 'featured.html')
            form = FormatForm({'canonical': True, 'explicit_start': True, 'explicit_end': True,
                               'default_style': 0, 'default_flow_style': 1, 'indent': 4, 
                               'width': 80, 'yaml_version': 1, 'show_version': True, 'events': False, 'tokens': False})
            template_values = {"form": form, "logout_url": users.create_logout_url(self.request.uri)}
        else:
            path = os.path.join(os.path.dirname(__file__), 'welcome.html')
            template_values = {"login_url": users.create_login_url(self.request.uri)}
        template_values["yaml_version"] = yaml.__version__    
        self.response.out.write(template.render(path, template_values))
    
    def post(self):
        user = users.get_current_user()

        content = self.request.get('content')
        events = None
        tokens = None
        node = None
        if user:
            path = os.path.join(os.path.dirname(__file__), 'featured.html')
            form = FormatForm(self.request.POST) # A form bound to the POST data
            if form.is_valid(): # All validation rules pass
                canonical = form.clean_data['canonical']
                default_style = form.clean_data['default_style']
                if default_style == '0':
                    default_style = None
                default_flow_style = form.clean_data['default_flow_style']
                if default_flow_style == '1':
                    default_flow_style = None
                elif default_flow_style == '2':
                    default_flow_style = False
                else:
                    default_flow_style = True
                indent = int(form.clean_data['indent'])
                width = int(form.clean_data['width'])
                explicit_start = form.clean_data['explicit_start']
                explicit_end = form.clean_data['explicit_end']
                show_version = form.clean_data['show_version']
                if show_version:
                    if form.clean_data['yaml_version'] == '0':
                        yaml_version=(1, 0)
                    else:
                        yaml_version=(1, 1)
                else:
                    yaml_version = None
                show_events = form.clean_data['show_events']
                show_tokens = form.clean_data['show_tokens']
                show_node = form.clean_data['show_node']
            else:
                self.response.out.write("Error: form is invalid.")
                return
        else:
            path = os.path.join(os.path.dirname(__file__), 'welcome.html')
            canonical = True
            default_style = '"'
            default_flow_style = False
            indent = 4
            width = 80
            explicit_start = True
            explicit_end = True
            yaml_version=(1, 1)
            show_events = False
            show_tokens = False
            show_node = False
            
        try:
            document = yaml.load(content)
            result = yaml.dump(document, default_style=default_style, default_flow_style=default_flow_style,
                               canonical=canonical, indent=indent, width=width,
                               explicit_start=explicit_start, explicit_end=explicit_end, version=yaml_version)
            """ 1 < indent < 10, width > 20"""
            
            if show_events:
                events = "\n".join(str(event) for event in yaml.parse(content))
            if show_tokens:
                tokens = "\n".join(str(token) for token in yaml.scan(content))
            if show_node:
                node = str(yaml.compose(content))
                splitted = node.split("),")
                node = "),\n".join(splitted)
            valid = True
        except Exception, e:
            valid = False
            result = "The document is not valid YAML:\n%s\n%s" % (e, content)
        # save
        attempt = Attempt(author=user, content=content, valid=valid)
        attempt.put()
        #
        counter = Attempt.all().count()
        if user:
            template_values = {"form": form, "node": node, "events": events,
                               "tokens": tokens, "counter": counter, "logout_url": users.create_logout_url(self.request.uri)}
        else:  
            template_values = {"login_url": users.create_login_url(self.request.uri)}
        template_values["result"] = result
        template_values["content"] = content
        template_values["yaml_version"] = yaml.__version__
        self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication(
                                      [('/', MainPage)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()