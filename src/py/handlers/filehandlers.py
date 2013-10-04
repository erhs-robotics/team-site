import sys
sys.path.append("./src/py/lib/db/")

import urllib

from appbase import Handler
from google.appengine.ext import db

from google.appengine.ext import blobstore
from google.appengine.ext import webapp
from google.appengine.ext.webapp import blobstore_handlers

class FileListHandler(webapp.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/uploadfile')
        self.response.out.write('<html><body>')
        self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
        self.response.out.write("""Upload File: <input type="file" name="file"><br> <input type="submit" name="submit" value="Submit"> </form></body></html>""")

        for b in blobstore.BlobInfo.all():
            delete_url = '/deletefile/%s' % b.key()
            self.response.out.write('<li><a href="/file/%s' % str(b.key()) + '">' + str(b.filename) + '</a>')
            self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % delete_url)
            self.response.out.write('<input type="submit" name="submit" value="Delete"> </form>')

class UploadFileHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')
        blob_info = upload_files[0]
        self.redirect('/filelist')

class DeleteFileHandler(webapp.RequestHandler):
	def post(self, blob_key):
		blob_key = str(urllib.unquote(blob_key))
		blobstore.BlobInfo.get(blob_key).delete()
		self.redirect('/filelist')

class ServeFileHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, blob_key):
        blob_key = str(urllib.unquote(blob_key))
        if not blobstore.get(blob_key):
            self.error(404)
        else:
            self.send_blob(blobstore.BlobInfo.get(blob_key), save_as=True)
