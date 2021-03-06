#!/usr/bin/env python
import sys
sys.path.append("./src/py/lib/")

import webapp2
import os
import jinja2
import cgi
from cookie import authenticate_cookie
from database import get_user
from collections import namedtuple
from database import gravatar, get_user
import calendar
import logging
from google.appengine.ext import db


def guess_autoescape(template_name):
    if template_name is None or '.' not in template_name:
        return False
    if template_name == "blog.html" or template_name == "index.html" or template_name == "viewpost.html":
        return False
    ext = template_name.rsplit('.', 1)[1]
    if ext in ('html'):
        return False
    return ext in ('htm', 'xml')

template_dir = os.path.join(os.path.dirname(__file__), '../../templates')
env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                         autoescape=guess_autoescape,
                         extensions=['jinja2.ext.autoescape'])
                        
class Handler(webapp2.RequestHandler):
    def login(self):
        cookie = self.request.cookies.get("user_id")
        user = get_user(authenticate_cookie(cookie))
        self.user = user        
        
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = False
        try:
            t = env.get_template(template)
            t = t.render(params)
        except:
            pass      
        
        return t
    
    def execute_error(self, error):
		
		self.render(error[0], **error[1])

    def render(self, template, **kw):
        kw['gravatar'] = gravatar
        kw['get_user'] = get_user
        kw['calendar'] = calendar
        kw['posts']    = list(db.GqlQuery("SELECT * FROM Post ORDER BY created DESC"))
        kw['min']      = min
        v = self.render_str(template, **kw)
        if v == False:# v will be false if the page was not found
            self.error(404)
        else:
            self.write(self.render_str(template, **kw))





