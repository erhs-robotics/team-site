import sys
sys.path.append("./src/py/lib/db/")

from handlerbase import Handler
from google.appengine.ext import db
from database import *
from os.path import isfile
from collections import namedtuple
import flickr

MemberTuple = namedtuple('Member', ['name', 'intime', 'outtime'])
Album = namedtuple("Album", ['albumid', 'name', 'date', 'cover'])
Photo  = namedtuple("Photo", ['name', 'url'])
request = flickr.getRequester(api_key=flickr.API_KEY, format="json", nojsoncallback="1")

def get_page(resource):
    pages = db.GqlQuery("SELECT * FROM Page WHERE location=:1 LIMIT 1", resource)
    pages = list(pages)
    if pages:
        return pages[0]
    else:
		return None	

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
        if not isfile("templates/" + page_location): page_location = "/generic.html" #resource.split("/")[0] + "/generic.html"
        nav_file = resource.split("/")[0] + "/nav.html"
        self.render(page_location, location=resource, page=page, user=self.user, nav_file=nav_file)
                
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
					
class ViewPostHandler(Handler):
	def get(self, resource):
		self.login()        
		if resource.isdigit():
			post = Post.get_by_id(int(resource))
			if post:
				self.render("viewpost.html", user = self.user, 
											post = post)
											
class GalleryHandler(Handler):
	def get(self, resource):			
		self.login()
		sets = request(method="flickr.photosets.getList", user_id=flickr.GROUP_ID)
		if sets == None:
			self.render("gallery.html", user=self.user, error=True)
			return
			
		albums = []
		#Album = namedtuple("Album", ['albumid', 'name', 'date', 'cover'])
		for s in sets["photosets"]["photoset"]:
			url = flickr.imageUrl(s["farm"], s["server"], s["primary"], s["secret"])			
			a = Album(s["id"], s["title"]["_content"], s["date_create"], url)
			albums.append(a)
			
		name = ""
		featured = []
		if resource == None or resource == "/": 
			resource = albums[0].albumid
			name = "Featured"
		else:
			resource = resource[1:]
			info = request(method="flickr.photosets.getInfo", photoset_id=resource)
			print info
			name = info["photoset"]["title"]["_content"]		
		
		
		photoset = request(method="flickr.photosets.getPhotos", photoset_id=resource)					
		for photo in photoset["photoset"]["photo"]:
			url = flickr.imageUrl(photo["farm"], photo["server"], photo["id"], photo["secret"])
			print url
			featured.append(Photo(photo["title"], url))
			if name == "Featured" and len(featured) == 8: break
		
		self.render("gallery.html", user=self.user, albums=albums, featuredname=name, featured=featured,
					error=False)
					
class AttendanceLogHandler(Handler):	
	def get_name(self, members_db, idstr):
		for member in members_db:
			if member.idstr == idstr:
				return member.name

	def get(self, resource):
		self.login()
		if not self.user.isadmin:
			self.redirect("/login")
			return
		year = 0
		month = 0
		day = 0		
		
		try:
			year = int(resource[:4])
			month = int(resource[4:6])
			day = int(resource[6:])
		except:
			self.redirect("/")
		
		attendance_list = list(db.GqlQuery("SELECT * FROM Attendance"))
		attendance = None
		for x in attendance_list:
			d = x.date
			print "Looking for: (%s, %s, %s)" % (year, month, day)
			print "Found: (%s, %s, %s)" % (d.year, d.month, d.day)			
			if d.year == year and d.month == month and d.day == day:
				attendance = x
				break
		if attendance == None:
			self.render("message.html", message="No attendance found", redirect=False)
			return				
		
		members_db = list(db.GqlQuery("SELECT * FROM Member"))
		members = []
		for s in attendance.punchcard:
			parts = s.split("|")
			in_time = parts[1] if len(parts) >= 2 else "error"
			out_time = parts[2] if len(parts) == 3 else "never punched out"			
			name = self.get_name(members_db, parts[0])
			members.append(MemberTuple(name, in_time, out_time))
		members = sorted(members, key = lambda x: x.name)
		self.render("attendance.html", members=members, user=self.user)
