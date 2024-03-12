function set_urls(){
    var stream_url = window.location.protocol + "//" +  window.location.hostname + ":8013/stream";
    document.getElementById('video_stream').src = stream_url;
}

function setPreviewSize(){
	var img = document.getElementById('video_stream');

	var width  = (window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth) - 20;
	const height = (window.innerHeight|| document.documentElement.clientHeight|| document.body.clientHeight) - 60;
    if(width > 1280){
        width = 1280;
    }
	img.style.width = width + 'px';
	img.style.height = 'auto';

	if(img.height > height){
		img.style.height = height + 'px';
		img.style.width = 'auto';
	}

	document.getElementById('container').setAttribute("style","width:" + img.clientWidth + "px");
}


window.onload = function() {
    set_urls();
    setPreviewSize();
}

