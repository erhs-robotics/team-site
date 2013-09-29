#!/usr/bin/env python
import sys
sys.path.append("./src/py/handlers/")

from fronthandlers import *
from backhandlers import *
from formhandlers import *
from filehandlers import *
import webapp2

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
							   ('/resources/punchclock', PunchClockHandler),
							   ('/addmember', AddMemberHandler),
							   ('/attendance/(\d+)', AttendanceLogHandler),
							   ('/gallery(/.*)?', GalleryHandler),
							   ('/filelist', FileListHandler),
							   ('/uploadfile', UploadFileHandler),
							   ('/deletefile/([^/]+)?', DeleteFileHandler),
                               ('/file/([^/]+)?', ServeFileHandler),
                               ('/(.+)', GenericHandler)],
                               debug=True)
