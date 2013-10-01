import sys
sys.path.append("./src/py/lib/db/")
sys.path.append("./src/py/lib/")

from appbase import Handler
from google.appengine.api import images
from google.appengine.ext import db
from database import *
from password import *
from cookie import *

import datetime

def get_page(resource):
    pages = db.GqlQuery("SELECT * FROM Page WHERE location=:1 LIMIT 1", resource)
    pages = list(pages)
    if pages:
        return pages[0]
    else: return None

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
			if self.user:
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
			if self.user:
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
        

class NewPageHandler(Handler):
    def render_form(self, title="", location="", content="", error="",user=None):
        self.render("newpage.html", title=title, location=location, content=content, error=error, user=user)
    def get(self):
        self.login()
        
        if self.user:
            self.render_form(user = self.user)
        else:
            self.redirect("/login")
    def post(self):
        self.login()               
        if self.user:            
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
        if self.user:
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
        
        if self.user:        
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
		
class PunchClockHandler(Handler):
	def get(self):
		self.login()
		if self.user and self.user.isadmin:
			cookie = self.request.cookies.get("inorout")
			if cookie != "out": cookie = "in"		
			self.render("/resources/punchclock.html", user=self.user, inorout=cookie, getname=False)
		else:
			self.redirect("/login")
		
	def getid(self, x): return x.split("|")[0]
	
	def get_today(self):
		attendance = list(db.GqlQuery("SELECT * FROM Attendance"))
		today = None
		t = self.request.get("time")
		year = int(t[:4])
		month = int(t[4:6])
		day = int(t[6:8])
		now = datetime.date(year, month, day)
		for day in attendance:
			if now == day.date: today = day
		if today == None:
			today = Attendance(date = now, clockin = [], clockout = [])			
			today.put()
			
		return today
		
	def get_time(self):		
		return self.request.get("time")[8:]
		
	def punched_in(self, idstr, attendance):
		for x in attendance.punchcard:
			parts = x.split("|")
			if parts[0] == idstr and len(parts) == 2:
				return True
		return False
		
	def punched_out(self, idstr, attendance):
		ret = False
		for x in attendance.punchcard:
			parts = x.split("|")
			if parts[0] == idstr and len(parts) == 3:
				ret = True
			elif parts[0] == idstr and len(parts) == 2:
				ret = False
		return ret
		
	def get_name(self, idstr):
		members = list(db.GqlQuery("SELECT * FROM Member"))
		member = None
		for x in members:
			if x.idstr == idstr: member = x.name
		if member == None:
			x = self.request.get("name")
			if x != "":
				member = x
				if len(idstr) == 9:
					newmember = Member(name=member, idstr=idstr)
					newmember.put()
		return member		
		
	def validate(self, idstr, name, inorout, attendance):
		if not len(idstr) in [9,6] : # ivalid id
			getname = True if self.request.get("name") != "" else False
			data = {"idstr":idstr, "inorout":inorout, "error":"Invalid ID!", "getname":getname, "name":name}
			if getname: data["name"] = name
			return ("/resources/punchclock.html", data)
		if name is None:
			data = {"idstr":idstr, "inorout":inorout, "name":"", "getname":True,
					"error":"That id is not currently in our system. Please enter your name"}
			return ("/resources/punchclock.html", data)
		if name == "":
			data = {"idstr":idstr, "inorout":inorout, "name":name, "error":"Please enter a name"}
			return ("/resources/punchclock.html", data)
		if inorout == "in" and self.punched_in(idstr, attendance):
			data = {"error":"%s has already punched in!" % name}
			return ("/resources/punchclock.html", data)
		if inorout == "out" and self.punched_out(idstr, attendance):
			data = {"error":"%s has already punched out!" % name}
			return ("/resources/punchclock.html", data)
		if inorout == "out" and not self.punched_in(idstr, attendance):
			data = {"error":"%s cannot punch out. You never punched in!" % name}
			return ("/resources/punchclock.html", data)
		t = self.request.get("time")
		if len(t) != 12 or not t.isdigit():
			data = {"error":"Invalid time!" % name}
			return ("/resources/punchclock.html", data)
			
		
	def post(self):			
		self.login()
		if self.user and self.user.isadmin:
			inorout = self.request.get("inorout")
			idstr = self.request.get("idstr")			
			attendance = self.get_today()
			name = self.get_name(idstr)
			error = self.validate(idstr, name, inorout, attendance)			
			if error: self.execute_error(error); return
			time = self.get_time()
			if inorout == "in":
				attendance.punchcard.append(idstr + "|" + time)				
			else:
				for i in range(len(attendance.punchcard)):
					parts = attendance.punchcard[i].split("|")
					if idstr == parts[0] and len(parts) == 2:
						attendance.punchcard[i] += "|" + time
						break
			attendance.put()
			message="Succsess! %s punched %s at %s" % (name, inorout, time)
			self.response.headers.add_header('Set-Cookie', str('inorout=%s'%inorout))			
			self.render("message.html", message=message, redirect=True)			
		else:
			self.redirect("/login")
