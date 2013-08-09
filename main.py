#!/usr/bin/env python
import sys
sys.path.append("./lib/")
sys.path.append("./lib/db/")

import webapp2
import urllib
from cookie import *
from password import *
from handlerbase import Handler
from google.appengine.api import images
from google.appengine.ext import db
from database import *
import json
import logging
import datetime

def get_page(resource):
    pages = db.GqlQuery("SELECT * FROM Page WHERE location=:1 LIMIT 1", resource)
    pages = list(pages)
    if pages:
        return pages[0]
    else:
		return None
		
##########################
### FRONTENDS HANDLERS ###
##########################

class MainHandler(Handler):
    def get(self):
        self.login()            
        posts = list(db.GqlQuery("SELECT * FROM Post ORDER BY created DESC"))
        slides = Slide.all()
        self.render("index.html", user = self.user, post = posts, slides=slides)
        
class GenericHandler(Handler):
    def get(self, resource):
        self.login()
        page_location = resource + ".html"
        page = get_page(resource)
        if page != None: page_location = "generic.html"
        self.render(page_location, page=page, user=self.user)
                
class BlogHandler(Handler):
    def getTotalPosts(self, post_list):
        post_count = 0
        for post in post_list:
             post_count += 1
        return post_count
    def get(self, resource):
        self.login()
    
        #user = User(username="admin", password=make_pw_hash('admin', 'admin1234'), isadmin=True)
        #user.put()
        
        posts = Post.all()
        
        currentPage = int(resource)
        POSTS_PER_PAGE = 5
        TOTAL_POSTS = self.getTotalPosts(list(posts))
        TOTAL_PAGES = TOTAL_POSTS / POSTS_PER_PAGE
        if TOTAL_POSTS % POSTS_PER_PAGE != 0:
			TOTAL_PAGES += 1
			
        hasPreviousPage = False
        hasNextPage = False
		
        if currentPage != 1: hasPreviousPage = True
        if currentPage != TOTAL_PAGES: hasNextPage = True
        
        posts.order("-created")
        active_posts = []
        for post in posts.run(limit=POSTS_PER_PAGE, offset=(POSTS_PER_PAGE * (currentPage - 1))):
			 active_posts.append(post)

        self.render("blog.html", user=self.user, posts=active_posts, TOTAL_POSTS=TOTAL_POSTS, TOTAL_PAGES=TOTAL_PAGES, 
					hasNextPage=hasNextPage, hasPreviousPage=hasPreviousPage, currentPage=currentPage)               
   
class ViewPostHandler(Handler):
    def get(self, resource):
        self.login()        
        
        if resource.isdigit():
            post = Post.get_by_id(int(resource))
                        
        if post:
            self.render("viewpost.html", user = self.user, post = post)
     
class ContactHandler(Handler):
    def get(self):
        self.login()  
        messages = db.GqlQuery("SELECT * FROM Message")
        self.render("contact.html", user = self.user, messages = list(messages))
    def post(self):
        self.login()
        messages = db.GqlQuery("SELECT * FROM Message")
        sender_name = self.request.get('sender_name')
        sender_email = self.request.get('sender_email')
        sender_message = self.request.get('sender_message')
        if sender_message != "":
            newMessage = Message(name=sender_name, email=sender_email, message=sender_message)
            newMessage.put()
        self.render("contact.html", user=self.user, messages = list(messages))
        
class ControlHandler(Handler):
	def get(self):
		self.login()
		slides = Slide.all()
		sponsors = Sponsor.all()
		self.render("control.html", user=self.user, slides=slides, sponsors=sponsors)
	def post(self):
		self.login()
		slideshow_submit = self.request.get("slideshow_submit")
		createuser_submit = self.request.get("createuser_submit")
		sponsors_submit = self.request.get("sponsors_submit")
		if slideshow_submit:
			if can_post(self.user):
				image = self.request.get("image")
				caption = self.request.get("caption")
				link = self.request.get("link")
				if image and caption:
					slide = Slide()
					image = images.resize(image, 440, 270)
					slide.image = db.Blob(image)
					slide.caption = caption
					slide.link = link
					slide.put()
					self.redirect("/control")
				else:
					self.render("control.html", user=self.user, slides=Slide.all(), 
								image=image, caption=caption, link=link, 
								error="Please provide an image and a caption")
		if createuser_submit:
			if self.user and self.user.isadmin:
				username = self.request.get('username')
				password = self.request.get('password')
				verify = self.request.get('verify')
				email = self.request.get('email')            
				fullname = self.request.get('fullname')          
				
				v_user = match(USER, username)
				v_pass = match(PASS, password)
				v_verify = None
				if password == verify:
					v_verify = 1       

				v_email = 1
				if email: v_email = match(EMAIL, email)

				v_existing_user = db.GqlQuery('SELECT * FROM User WHERE username=:1', username)
				v_existing_user = v_existing_user.count()

				if v_user and v_pass and v_verify and v_email and v_existing_user < 1:
					password = make_pw_hash(username, password)
					newuser = User(username=username, password=password, email = email, isadmin=False)
					if fullname: newuser.fullname = fullname
					newuser.put()                
					self.redirect('/control')
				else:
					m_user = ''
					m_pass = ''
					m_verify = ''
					m_email = ''
					if not v_user: m_user = 'not a valid username.'            
					if not v_pass: m_pass = 'not a valid password.'
					if not v_verify: m_verify = 'passwords do not match.'
					if not v_email: m_email = 'not a valid email.'
					if v_existing_user > 0: m_user = 'That user already exists.'
					self.render("members.html", user = self.user,
								email = m_email,
								username = m_user,
								password =  m_pass,
								verify = m_verify,
								mail = email,
								fullname = fullname,
								display = "block")
		if sponsors_submit:
			if can_post(self.user):
				name = self.request.get("name")
				link = self.request.get("link")
				image = self.request.get("image")
				level = self.request.get("level")
				if name and image:
					sponsor = Sponsor()
					sponsor.image = db.Blob(image)
					sponsor.name = name
					sponsor.link = link
					sponsor.level = level
					sponsor.put()
					self.redirect("/control")
				else:
					self.render("control.html", user=self.user, slides=Slide.all(),
								image=image, name=name, link=link,
								error="Please provide an image and a name")
								
class SponsorsHandler(Handler):
	def get(self):
		self.login()
		sponsors = Sponsor.all()
		platinum, gold, silver, bronze = [], [], [], []
		for sponsor in sponsors:
			if sponsor.level == "Platinum":
				platinum.append(sponsor)
			elif sponsor.level == "Gold":
				gold.append(sponsor)
			elif sponsor.level == "Silver":
				silver.append(sponsor)
			else:
				bronze.append(sponsor)
		self.render("sponsors.html", user=self.user, platinum=platinum,
					gold=gold, silver=silver, bronze=bronze)
			
#########################  
### BACKENDS HANDLERS ###
#########################

class LoginHandler(Handler):
     def get(self):
        self.login()
        self.render('login.html', user = self.user, remember = "false")

     def post(self):        
        username = self.request.get('username')
        password = self.request.get('password')
        remember = self.request.get('remember')       
        
        user = db.GqlQuery('SELECT * FROM User WHERE username=:1 LIMIT 1', username)        

        if user.count() > 0 :
            if valid_pw(username, password, user[0].password):
                user_id = make_secure_val(str(user[0].key().id()))
                header ="user_id=%s" % user_id
                if remember == "true": header += "; expires=Wednesday, 01-Aug-2040 08:00:00 GMT"
                self.response.headers.add_header('Set-Cookie', header)
                self.redirect('/')
            else:
                self.render('login.html',username=username, error = "invalid password", remember=remember)
        else:
            self.render('login.html',username=username, error = "invalid login")

class LogoutHandler(Handler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
        self.redirect("/login")

class NewpostHandler(Handler):
    def render_form(self, subject="", content="", error="",user=None):
        self.render("newpost.html", subject=subject, content=content, error=error, user=user)
    def get(self):
        self.login()
        if self.user:
            self.render_form(user = self.user)
        else:
            self.redirect("/login")
    def post(self):
        self.login()               
        if self.user:            
            subject = self.request.get("subject")
            content = self.request.get("content")

            if subject and content:
                post = Post(subject=subject, content=content, username = self.user.username, user = self.user.key().id())            
                post.put()                
                self.redirect("/blog/1")
            else:
                self.render_form(subject, content, "Please provide a title and content", user=self.user)

class DeletepostHandler(Handler):    
    def post(self):
        self.login()            
        if self.user:
            post = self.request.get("post")
            if post.isdigit():
                post = Post.get_by_id(int(post))
            else:
                post = None
            
            if post and (post.user == self.user.key().id() or self.user.isadmin):
                post.delete()
        
        self.redirect("/blog/1")
        
class EditPostHandler(Handler):
    def get(self, resource):
        self.login()        
        
        if self.user and resource.isdigit():
            post = Post.get_by_id(int(resource))      
            
            if post and (post.user == self.user.key().id() or self.user.isadmin):
                self.render("newpost.html", user = self.user, 
                                            subject=post.subject, 
                                            content=post.content)
        else:
            self.redirect('/login')
            
    def post(self, ID):
        self.login()
        
        if self.user and ID.isdigit():        
            post = Post.get_by_id(int(ID))           
            if post and (self.user.key().id() == post.user or self.user.isadmin):            
                subject = self.request.get("subject")
                content = self.request.get("content")            

                if subject and content:                
                    post.subject = subject
                    post.content = content        
                    post.put()
                    self.redirect("/blog/1")              
                else:
                    self.render_form(subject, content, "Please provide a title and content", user=user)
        else:
            self.redirect("/login")
        
class ImageHandler(Handler):
    def get(self):
		imgId = self.request.get("img_id").split("?")[0]
		entity = db.get(imgId)
		if entity.image:
			self.response.headers['Content-Type'] = "image/jpg"
			self.response.out.write(entity.image)
		else:
			self.response.out.write("No Image")
            
class DeleteUserHandler(Handler):
    def post(self):
        self.login()
        del_user = self.request.get("user")
        if self.user and self.user.isadmin:
            if del_user.isdigit():
                del_user = User.get_by_id(int(del_user))
                if del_user:
                    del_user.delete()
                self.redirect("/about/members")
        else:
            self.redirect("/login")

class NewPageHandler(Handler):
    def render_form(self, title="", location="", content="", error="",user=None):
        self.render("newpage.html", title=title, location=location, content=content, error=error, user=user)
    def get(self):
        self.login()
        
        if can_post(self.user):
            self.render_form(user = self.user)
        else:
            self.redirect("/login")
    def post(self):
        self.login()               
        if can_post(self.user):            
            title = self.request.get("title")
            location = self.request.get("location")
            content = self.request.get("content")

            if title and location and content:
                page = Page(title=title, location=location, content=content)            
                page.put()                
                self.redirect("/" + location)
            else:
                self.render_form(title, location, content, "Please provide a title, location, and content", user=self.user)
     
class EditPageHandler(Handler):
    def render_form(self, title="", location="", content="", error="",user=None):
        self.render("newpage.html", title=title, location=location, content=content, error=error, user=user)
    def get(self, resource):
        self.login()        
        if can_post(self.user):
            page = get_page(resource)
            if page:
                self.render("newpage.html", user = self.user, 
											title = page.title,
											location = page.location,
											content = page.content,
											error = "")
        else:
            self.redirect('/login')     
    def post(self, resource):
        self.login()
        
        if can_post:        
            page = get_page(resource)
            if page:     
                title = self.request.get("title")
                location = self.request.get("location")
                content = self.request.get("content")              

                if title and location and content:                
                    page.title = title
                    page.location = location
                    page.content = content
                    page.put()
                    self.redirect("/" + resource)              
                else:
                    self.render_form(title, location, content, "Please provide a title, location, and content", user=user)
        else:
            self.redirect("/login")
		
class DeleteEntityHandler(Handler):
    def post(self):
        self.login()
        entity_key = self.request.get("entity")
        if self.user and self.user.isadmin:
            if entity_key:
                del_entity = db.get(entity_key)
                if del_entity:
                    del_entity.delete()
                self.redirect(self.request.host_url)
        else:
            self.redirect("/login")
            
app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/blog/(\d+)', BlogHandler),
                               ('/login', LoginHandler),
                               ('/logout', LogoutHandler),
                               ('/newpost', NewpostHandler),
                               ('/deletepost', DeletepostHandler),
                               ('/editpost/(\d+)', EditPostHandler),
                               ('/viewpost/(\d+)', ViewPostHandler),                              
                               ('/deleteuser', DeleteUserHandler),                                                         
                               ('/newpage', NewPageHandler),
                               ('/editpage/(.+)', EditPageHandler),
							   ('/image', ImageHandler),
							   ('/control', ControlHandler),
							   ('/sponsors', SponsorsHandler),
							   ('/deleteentity', DeleteEntityHandler),
                               ('/(.+)', GenericHandler)],
                               debug=True)
