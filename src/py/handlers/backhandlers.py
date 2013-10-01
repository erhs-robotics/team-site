import sys
sys.path.append("./src/py/lib/db/")
sys.path.append("./src/py/lib/")

from google.appengine.ext import db
from appbase import Handler
from database import *
from cookie import *

class LogoutHandler(Handler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
        self.redirect("/login")
        
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

class AddMemberHandler(Handler):
	def post(self):
		self.login()
		name = self.request.get("name")
		idstr = self.request.get("idstr")
		inorout = self.request.get("inorout")
		member = Member(name = name, idstr = idstr)
		member.put()
		data = urllib.urlencode({"idstr":idstr, "inorout":inorout})
		app.post("/punch", data)
