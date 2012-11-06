var GROUP_ID = 158519044177128;
var PAGE_ID  = 184052998344999;
var month=new Array();
month[0]="January";
month[1]="February";
month[2]="March";
month[3]="April";
month[4]="May";
month[5]="June";
month[6]="July";
month[7]="August";
month[8]="September";
month[9]="October";
month[10]="November";
month[11]="December";
var debug;

function getGroupPhotos(id) {
	var xmlHttp = new XMLHttpRequest();
  xmlHttp.open( "GET", "http://graph.facebook.com/fql?q=SELECT pid FROM photo_tag WHERE subject=" + id, false);
  xmlHttp.send( null );
  return $.parseJSON(xmlHttp.responseText);	
}

function getPhoto(id) {
	var xmlHttp = new XMLHttpRequest();
  xmlHttp.open( "GET", "http://graph.facebook.com/fql?q=SELECT pid, src_big, created FROM photo WHERE pid=\"" + id + "\"", false);
  xmlHttp.send( null );
  return $.parseJSON(xmlHttp.responseText);	
	
}

function getPageAlbums(id) {
	var xmlHttp = new XMLHttpRequest();
  xmlHttp.open( "GET", "http://graph.facebook.com/" + id + "/albums?fields=id,name", false);
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
	var group_wall = new Array();
	for(i=0;i<group_photos.data.length;i++) {
		var src = getPhoto(group_photos.data[i].pid);
		group_wall.push({"src" :src.data[0].src_big, "created" : new Date(src.data[0].created * 1000 /* x1000 for conversion*/)})
	}
	group_wall.sort(function(a,b){return new Date(b.created - a.created)});
	photos.push({"name": "Group Wall Photos", "images": group_wall});

	var page_albums = getPageAlbums(PAGE_ID);//for page's albums
	//store the page's album photos
	for(i=0;i<page_albums.data.length;i++) {
		var photo = getPhotosFromAlbum(page_albums.data[i].id);
		var album = new Array();
		for(a=0;a<photo.data.length;a++) {
			album.push({"src" : photo.data[a].source, "created" : new Date(photo.data[a].updated_time)});
		}
		album.sort(function(a,b){return new Date(b.created - a.created)});
		photos.push({"name": page_albums.data[i].name, "images": album});
	}


	
	debug = photos;
	
	for(i=0;i<photos.length;i++) {
		var album = $("<div/>", {"class": "content, album"});
		album.append($("<h2>" + photos[i].name + "</h2>"));
		for(x=0;x<photos[i].images.length;x++) {
			//<div id="Homecoming-2012" class="content" style="border: 1px solid black; height: 240px; overflow: auto">
			//	<h2>Homecoming 2012</h2>
			//</div>	
			//var date = month[photos[i].created.getMonth()] + " " + photos[i].created.getDate() + ", " + photos[i].created.getFullYear();
			var img = $("<img/>", { "src" : photos[i].images[x].src });
			var gallery_photo = $("<a/>", {"rel" : "group", "href" : photos[i].src, "class" : "gallery_photo"}).append(img);
			album.append(gallery_photo);			
		}

		$("#img_gallery").append(album);
		

	}



}
