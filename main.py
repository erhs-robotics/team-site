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

### FRONTENDS HANDLERS ###

class MainHandler(Handler):
    def get(self):
        self.login()            
        posts = list(db.GqlQuery("SELECT * FROM Post ORDER BY created DESC"))
        self.render("index.html", user = self.user, post = posts)       
        
class AboutHandler(Handler):
	def get(self):
		self.login()
		self.render("about.html", user=self.user)
		
class HistoryHandler(Handler):
	def get(self):
		self.login()
		self.render("history.html", user=self.user)
		
class SubteamsHandler(Handler):
	def get(self):
		self.login()
		self.render("subteams.html", user=self.user)

class OutreachHandler(Handler):
	def get(self):
		self.login()
		self.render("outreach.html", user=self.user)
		
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
        
        self.render("members.html", user = self.user, users=members, display="none", programmers = programmers,
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
                self.redirect('/members')
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

class MentorsHandler(Handler):
	def get(self):
		self.login()
		self.render("mentors.html", user=self.user)
		
class CompetitionsHandler(Handler):
	def get(self):
		self.login()
		self.render("competitions.html", user=self.user)
		
class WebsiteHandler(Handler):
	def get(self):
		self.login()
		self.render("website.html", user=self.user)
		
class FirstHandler(Handler):
    def get(self):
        self.login()
        self.render("first.html", user = self.user)
        
class FirstGameHandler(Handler):
	def get(self):
		self.login()
		self.render("firstgame.html", user=self.user)
        
class VexHandler(Handler):
	def get(self):
		self.login()
		self.render("vex.html", user = self.user)
		
class MucHandler(Handler):
	def get(self):
		self.login()
		self.render("muc.html", user = self.user)
		
class BlogHandler(Handler):
    def get(self):
        self.login()
        
        
        #user = User(username="admin", password=make_pw_hash('admin', 'admin1234'), isadmin=True)
        #user.put()
        
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")      
        self.render("blog.html", user = self.user, posts = list(posts))
        
class SponsorsHandler(Handler):
    def get(self):
        self.login()        
        self.render("sponsors.html", user = self.user)
        
class GalleryHandler(Handler):
    def get(self):
        self.login()
        self.render("gallery.html", user = self.user)

class ResourcesHandler(Handler):
    def get(self):
        self.login()        
        self.render("resources.html", user = self.user)
        
class ParentsHandler(Handler):
	def get(self):
		self.login()
		self.render("parents.html", user = self.user)

class DocsHandler(Handler):
	def get(self):
		self.login()
		self.render("docs.html", user = self.user)

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
                self.redirect("/blog")
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
        
        self.redirect("/blog")
        
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
                    self.redirect("/blog")              
                else:
                    self.render_form(subject, content, "Please provide a title and content", user=user)
        else:
            self.redirect("/login")
        
class ImageHandler(Handler):
    def get(self):
        user = db.get(self.request.get("id"))
        if user.userimage:
            self.response.headers['Content-Type'] = "image/png"
            self.response.out.write(user.userimage)
        else:
            self.error(404)
            
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
                
                if profile.team == "Programming":
                    prog = 'selected="selected"'
                elif profile.team == "Mechanical":
                    mec  = 'selected="selected"'
                elif profile.team == "Outreach":
                    out  = 'selected="selected"'
                elif profile.team == "Management":
                    mang = 'selected="selected"'
                    
                currentProjects = self.genCurrentProjects(profile)
                pastProjects    = self.genPastProjects(profile)
                
                
                self.render("editprofile.html", user = self.user, profile = profile,
                            currentProjects=currentProjects ,pastProjects=pastProjects,
                            prog=prog, mec=mec, out=out, mang=mang, display="none")
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
                    
                    if profile.team == "Programming":
                        prog = 'selected="selected"'
                    elif profile.team == "Mechanical":
                        mec  = 'selected="selected"'
                    elif profile.team == "Outreach":
                        out  = 'selected="selected"'
                    elif profile.team == "Management":
                        mang = 'selected="selected"'
                        
                    self.render("editprofile.html", user = self.user, profile = profile,
                            currentProjects=currentProjects ,pastProjects=pastProjects,
                            prog=prog, mec=mec, out=out, mang=mang, display="block",
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
                self.redirect("/members")
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

app = webapp2.WSGIApplication([('/', MainHandler),
							   ('/about', AboutHandler),
									('/about/history', HistoryHandler),
									('/about/subteams', SubteamsHandler),
									('/about/outreach', OutreachHandler),
									('/about/members', MembersHandler),
									('/about/mentors', MentorsHandler),
									('/about/website', WebsiteHandler),
							   ('/competitions', CompetitionsHandler),
								   ('/first',FirstHandler),
										#('/first/game', FirstGameHandler),
								   ('/vex', VexHandler),
										#('/vex/game', VexGameHandler),
								   ('/muc', MucHandler),
										#
                               ('/blog', BlogHandler),
                               ('/sponsors', SponsorsHandler),
                               ('/gallery', GalleryHandler),
                               ('/resources', ResourcesHandler),
									('/resources/parents', ParentsHandler),
									('/resources/docs', DocsHandler),
									('/resources/contact', ContactHandler),
                               ('/login', LoginHandler),
                               ('/logout', LogoutHandler),
                               ('/newpost', NewpostHandler),
                               ('/members', MembersHandler),
                               ('/deletepost', DeletepostHandler),
                               ('/editpost/(\d+)', EditPostHandler),
                               ('/image', ImageHandler),
                               ('/profile/(.+)', ProfileHandler),
                               ('/editprofile/(.+)', EditProfileHandler),
                               ('/deleteuser', DeleteUserHandler),
                               ('/updateprivileges', UpdatePrivilegesHandler),
							   ('/resources', ResourcesHandler),
                               ('/contact', ContactHandler),
							   ('/parents', ParentsHandler),
                               ('/viewpost/(\d+)', ViewPostHandler)],
                               debug=True)
