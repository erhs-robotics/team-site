var GROUP_ID = 158519044177128

function getGroupPhotos(id) {
	var xmlHttp = new XMLHttpRequest();
  xmlHttp.open( "GET", "http://graph.facebook.com/fql?q=SELECT pid FROM photo_tag WHERE subject=" + id, false);
  xmlHttp.send( null );
  return $.parseJSON(xmlHttp.responseText);	
}

function getPhoto(id) {
	var xmlHttp = new XMLHttpRequest();
  xmlHttp.open( "GET", "http://graph.facebook.com/fql?q=SELECT pid, src_small, src_big, owner FROM photo WHERE pid=\"" + id + "\"", false);
  xmlHttp.send( null );
  return $.parseJSON(xmlHttp.responseText);	
	
}

function loadGallery() {	
	var photos = getGroupPhotos(GROUP_ID);
	
	for(i=0;i<photos.data.length;i++) {
		var src = getPhoto(photos.data[i].pid);
		$("#img_gallery").append("<img src=\"" + src.data[0].src_big + "\">");
		

	}
	
	


}
