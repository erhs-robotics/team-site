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

CAN_POST     = 1
CAN_MAKEUSER = 2
IS_MEMBER    = 3

privileges = {CAN_POST : "can post", CAN_MAKEUSER : "can create users", IS_MEMBER : "is member"}

rand_word = ''

def get_page(resource):
    pages = db.GqlQuery("SELECT * FROM Page WHERE location=:1 LIMIT 1", resource)
    pages = list(pages)
    if pages:
        return pages[0]
    else:
		return None

### FRONTENDS HANDLERS ###

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
        if page or not page:
            self.render(page_location, location=resource, page=page, user=self.user)
        else:
            self.render(page_location, location=resource, user=self.user)
        
class MembersHandler(Handler):
    def get(self):        
        self.login()
        
        members = db.GqlQuery("SELECT * FROM User")
        members = list(members)    
        members = sorted(members, key=lambda member: member.username.lower())
        programmers = []
        mechies = []
        managers = []
        outreachers = []
        for member in members:
            if member.team == "Programming":
                programmers.append(member)
            elif member.team == "Mechanical" or member.team == None:
                mechies.append(member)
            if member.team == "Management":
                managers.append(member)
            if member.team == "Outreach":
                outreachers.append(member)
        
        self.render("about/members.html", user = self.user, users=members, display = "none", programmers = programmers,
					mechies = mechies, managers = managers, outreachers = outreachers)
        
    def post(self):
        self.login()        
        if self.user and CAN_MAKEUSER in self.user.privileges:
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
                newuser = User(username=username, password=password, email = email, isadmin=False, privileges=[IS_MEMBER])
                if fullname: newuser.fullname = fullname
                newuser.put()                
                self.redirect('/about/members')
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
                members = db.GqlQuery("SELECT * FROM User")
                members = list(members)    
                members = sorted(members, key=lambda member: member.username.lower())
                programmers = []
                mechies = []
                managers = []
                outreachers = []
                for member in members:
                    if member.team == "Programming":
                        programmers.append(member)
                    elif member.team == "Mechanical" or member.team == None:
                        mechies.append(member)
                    if member.team == "Management":
                        managers.append(member)
                    if member.team == "Outreach":
                        outreachers.append(member)
                self.render("members.html", user = self.user,
                            email = m_email,
                            username = m_user,
                            password =  m_pass,
                            verify = m_verify,
                            mail = email,
                            fullname = fullname,
                            display = "block",
                            users=members, programmers=programmers, mechies=mechies, managers=managers,
                            outreachers=outreachers)
        
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
                        
        #query = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
        #cursor = self.request.get('cursor')
        #if cursor: query.with_cursor(cursor)
        #posts = query.fetch(2)
        #cursor = query.cursor()
        
        #self.render("blog.html", user=self.user, posts=list(posts), cursor=cursor)
        
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
        
class ContactHandler(Handler):
    def get(self):
        self.login()  
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")      
        messages = db.GqlQuery("SELECT * FROM Message")# ORDER BY ID")
        self.render("contact.html", user = self.user, messages = list(messages), posts = list(posts))
    def post(self):
        self.login()
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")      
        messages = db.GqlQuery("SELECT * FROM Message")# ORDER BY ID")
        sender_name = self.request.get('sender_name')
        sender_email = self.request.get('sender_email')
        sender_message = self.request.get('sender_message')
        if sender_message != "":
            newMessage = Message(name=sender_name, email=sender_email, message=sender_message)
            newMessage.put()
        self.render("contact.html", user=self.user, messages = list(messages), posts = list(posts))
        
class ControlHandler(Handler):
	def get(self):
		self.login()
		slides = Slide.all()
		self.render("control.html", user=self.user, slides=slides)
	def post(self):
		self.login()
		if self.user and (CAN_POST in self.user.privileges or self.user.isadmin):
			slide = Slide()
			#image = self.request.get("image")
			image = self.request.get('image')
			caption = self.request.get("caption")
			link = self.request.get("link")
			if image and caption:
				image = images.resize(self.request.get('image'), 420, 270)
				slide.image = db.Blob(image)
				slide.caption = caption
				slide.link = link
				slide.put()
				self.redirect("/control")
			else:
				self.render("control.html", user=self.user, slides=Slide.all(), 
				            image=image, caption=caption, link=link, 
				            error="Please provide an image and a caption")
       
### BACKENDS HANDLERS ###

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
        
        if self.user and CAN_POST in self.user.privileges:
            self.render_form(user = self.user)
        else:
            self.redirect("/login")
        
    def post(self):
        self.login()               
        if self.user and CAN_POST in self.user.privileges:            
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
        if self.user and CAN_POST in self.user.privileges:
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
        
        if self.user and CAN_POST in self.user.privileges and resource.isdigit():
            post = Post.get_by_id(int(resource))      
            
            if post and (post.user == self.user.key().id() or self.user.isadmin):
                self.render("newpost.html", user = self.user, 
                                            subject=post.subject, 
                                            content=post.content)
        else:
            self.redirect('/login')
            
    def post(self, ID):
        self.login()
        
        if self.user and CAN_POST in self.user.privileges and ID.isdigit():        
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
		#entity = db.get(self.request.GET.get("img_id"))
		entity = db.get(db.Key(encoded=self.request.get("img_id")))
		if entity.image:
			self.response.headers['Content-Type'] = "image/jpg"
			self.response.out.write(entity.image)
		else:
			self.response.out.write("No Image")
            
class ProfileHandler(Handler):
    def get(self, res):
        self.login()
        profile = db.GqlQuery("SELECT * FROM User WHERE username=:1 LIMIT 1", res)
        profile = list(profile)
        if len(profile) == 1:
            self.render("profile.html", user = self.user, profile = profile[0], privileges = privileges)
        else:
            self.error(404)
            
class EditProfileHandler(Handler):
    def genCurrentProjects(self, profile):
        currentProjects = ""                                
        for i in range(len(profile.currentProjects)):
            if i == 0:
                currentProjects += profile.currentProjects[i]
            else:
                currentProjects += ", " + profile.currentProjects[i]
        return currentProjects
    
    def genPastProjects(self, profile):
        pastProjects = ""                                
        for i in range(len(profile.pastProjects)):
            if i == 0:
                pastProjects += profile.pastProjects[i]
            else:
                pastProjects += ", " + profile.pastProjects[i]
        return pastProjects       
    
    def get(self, res):
        self.login()
        profile = db.GqlQuery("SELECT * FROM User WHERE username=:1 LIMIT 1", res)
        profile = list(profile)
        if len(profile) == 1:
            profile = profile[0]
            if self.user.key().id() == profile.key().id():
                prog = ""
                mec  = ""
                out  = ""
                mang = ""
                ment = ""
                
                if profile.team == "Programming":
                    prog = 'selected="selected"'
                elif profile.team == "Mechanical":
                    mec  = 'selected="selected"'
                elif profile.team == "Outreach":
                    out  = 'selected="selected"'
                elif profile.team == "Management":
                    mang = 'selected="selected"'
                elif profile.team == "Mentoring":
					ment = 'selected="selected"'

                currentProjects = self.genCurrentProjects(profile)
                pastProjects    = self.genPastProjects(profile)
                
                
                self.render("editprofile.html", user = self.user, profile = profile,
                            currentProjects=currentProjects ,pastProjects=pastProjects,
                            prog=prog, mec=mec, out=out, mang=mang, ment=ment, display="none")
            else:
                self.redirect("/login")
        else:
            self.error(404)
    def post(self, res):
        self.login()        
        profile = db.GqlQuery("SELECT * FROM User WHERE username=:1 LIMIT 1", res)
        profile = list(profile)
        if len(profile) == 1 and self.user and self.user.key().id() == profile[0].key().id():
            profile = profile[0]
            quote        = self.request.get("quote")
            team         = self.request.get("team")
            currentProjs = self.request.get("currentProjects")
            pastProjs    = self.request.get("pastProjects")
            email        = self.request.get("email")
            fullname     = self.request.get("fullname")
            oldpass      = self.request.get("oldpass")
            newpass      = self.request.get("newpass")
            v_newpass    = self.request.get("v_newpass")
            
            currentProjs = currentProjs.split(',')
            for i in range(len(currentProjs)):
                currentProjs[i] = currentProjs[i].strip()
            
            pastProjs = pastProjs.split(',')
            for i in range(len(pastProjs)):
                pastProjs[i] = pastProjs[i].strip()
            
            profile.quote           = quote
            profile.team            = team
            profile.currentProjects = currentProjs
            profile.pastProjects    = pastProjs
            profile.email           = email
            
            if fullname: profile.fullname = fullname
            
            
            succsess = True
            if oldpass:
                v_old   = valid_pw(profile.username, oldpass, profile.password)
                v_valid = match(PASS, newpass)
                v_match = newpass == v_newpass
                if v_old and v_valid and v_match:
                    password = make_pw_hash(profile.username, newpass)
                    profile.password = password
                else:
                    succsess = False
                    m_old   = "incorrect password"
                    m_valid = "not a valid password"
                    m_match = "the passwords do not match"
                    if v_old:   m_old   = ""
                    if v_valid: m_valid = ""
                    if v_match: m_match = ""
                    currentProjects = self.genCurrentProjects(profile)
                    pastProjects    = self.genPastProjects(profile)
                    prog = ""
                    mec  = ""
                    out  = ""
                    mang = ""
                    ment = ""
                    
                    if profile.team == "Programming":
                        prog = 'selected="selected"'
                    elif profile.team == "Mechanical":
                        mec  = 'selected="selected"'
                    elif profile.team == "Outreach":
                        out  = 'selected="selected"'
                    elif profile.team == "Management":
                        mang = 'selected="selected"'
                    elif profile.team == "Mentoring":
						ment = 'selected="selected"'
                        
                    self.render("editprofile.html", user = self.user, profile = profile,
                            currentProjects=currentProjects ,pastProjects=pastProjects,
                            prog=prog, mec=mec, out=out, mang=mang, ment=ment, display="block",
                            old_err=m_old, valid_err=m_valid, match_err=m_match)                 
                        
                
            
            if succsess:
                profile.put()
                update_user(profile)
                self.redirect("/profile/%s" % res)
        else:
            self.redirect("/login")
            
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

class UpdatePrivilegesHandler(Handler):
    def post(self):
        self.login()
        page = "/"
        if self.user and self.user.isadmin:
            privs    = self.request.get_all("privileges")
            user_id = self.request.get("user")
            
            for i in range(len(privs)):
                if privs[i].isdigit():
                    privs[i] = int(privs[i])                
           
            if user_id.isdigit():
                user = get_user(int(user_id))
                if user:
                    user.privileges = privs
                    user.put()
                    update_user(user)
                    page = "/profile/%s" % user.username
                    
        self.redirect(page)
        
class ViewPostHandler(Handler):
    def get(self, resource):
        self.login()        
        
        if resource.isdigit():
            post = Post.get_by_id(int(resource))
                        
        if post:
            self.render("viewpost.html", user = self.user, post = post)
   
class NewPageHandler(Handler):
    def render_form(self, title="", location="", content="", error="",user=None):
        self.render("newpage.html", title=title, location=location, content=content, error=error, user=user)
	
    def get(self):
        self.login()
        
        if self.user and CAN_POST in self.user.privileges:
            self.render_form(user = self.user)
        else:
            self.redirect("/login")
        
    def post(self):
        self.login()               
        if self.user and CAN_POST in self.user.privileges:            
            title = self.request.get("title")
            location = self.request.get("location")
            content = self.request.get("content")

            if title and location and content:
                page = Page(title=title, location=location, content=content)            
                page.put()                
                self.redirect("/" + location)
            else:
                self.render_form(title, location, content, "Please provide a title and content", user=self.user)
     
class EditPageHandler(Handler):
    def render_form(self, title="", location="", content="", error="",user=None):
        self.render("newpage.html", title=title, location=location, content=content, error=error, user=user)
	
    def get(self, resource):
        self.login()        
        
        if self.user and CAN_POST in self.user.privileges:
            page = get_page(resource)
            
            if page:
                self.render("newpage.html", user = self.user, 
											title = page.title,
											location = page.location,
											content = page.content,
											error = "")
				
            #else:
            #    self.render("newpage.html", user=self.user, title="", location="", content="", error="")
        else:
            self.redirect('/login')
            
    def post(self, resource):
        self.login()
        
        if self.user and CAN_POST in self.user.privileges:        
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
                               ('/about/members', MembersHandler),
                               ('/deletepost', DeletepostHandler),
                               ('/editpost/(\d+)', EditPostHandler),
                               #('/image', ImageHandler),
                               ('/profile/(.+)', ProfileHandler),
                               ('/editprofile/(.+)', EditProfileHandler),
                               ('/deleteuser', DeleteUserHandler),
                               ('/updateprivileges', UpdatePrivilegesHandler),                            
                               ('/viewpost/(\d+)', ViewPostHandler),
                               ('/newpage', NewPageHandler),
                               ('/editpage/(.+)', EditPageHandler),
							   ("/image", ImageHandler),
							   ("/control", ControlHandler),
							   ('/deleteentity', DeleteEntityHandler),
                               ('/(.+)', GenericHandler)],
                               debug=True)
