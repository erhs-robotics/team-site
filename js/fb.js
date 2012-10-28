var GROUP_ID = 158519044177128;
var PAGE_ID  = 184052998344999;

function getGroupPhotos(id) {
	var xmlHttp = new XMLHttpRequest();
  xmlHttp.open( "GET", "http://graph.facebook.com/fql?q=SELECT pid FROM photo_tag WHERE subject=" + id, false);
  xmlHttp.send( null );
  return $.parseJSON(xmlHttp.responseText);	
}

function getPhoto(id) {
	var xmlHttp = new XMLHttpRequest();
  xmlHttp.open( "GET", "http://graph.facebook.com/fql?q=SELECT pid, src, created FROM photo WHERE pid=\"" + id + "\"", false);
  xmlHttp.send( null );
  return $.parseJSON(xmlHttp.responseText);	
	
}

function getPageAlbums(id) {
	var xmlHttp = new XMLHttpRequest();
  xmlHttp.open( "GET", "http://graph.facebook.com/" + id + "/albums?fields=id", false);
  xmlHttp.send( null );
  return $.parseJSON(xmlHttp.responseText);	
}

function getPhotosFromAlbum(id) {
	var xmlHttp = new XMLHttpRequest();
  xmlHttp.open( "GET", "http://graph.facebook.com/" + id + "/photos", false);
  xmlHttp.send( null );
  return $.parseJSON(xmlHttp.responseText);		
}



function loadGallery() {	
	var group_photos = getGroupPhotos(GROUP_ID);//for the group's wall photos

	var photos = new Array();//for all photos

	//store the group's wall photos
	for(i=0;i<group_photos.data.length;i++) {
		var src = getPhoto(group_photos.data[i].pid);
		photos.push({ "src" :src.data[0].src, "created" : src.data[0].created })
	}

	var page_albums = getPageAlbums(PAGE_ID);//for page's albums
	//store the page's album photos
	for(i=0;i<page_albums.data.length;i++) {
		var photo = getPhotosFromAlbum(page_albums.data[i].id);
		for(a=0;a<photo.data.length;a++) {
			photos.push({"src" : photo.data[a].source, "created" : photo.data[a].updated_time});
		}
	}

	

	
	
	
	for(i=0;i<photos.length;i++) {
		
		$("#img_gallery").append("<img src=\"" + photos[i].src + "\">");
		

	}
	
	


}
