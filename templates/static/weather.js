function reload() {
    location.reload();
}


window.onload = function() {
    // Refresh every half an hour
    setTimeout(reload, 1800000);

    var video_element = document.getElementById("weather_video");
    var v_width = video_element.videoWidth;
    var v_height = video_element.videoHeight;
    console.log("start:" + v_width + ", " + v_height);



//    var video_element = document.getElementById("weather_video");
//    video_element.addEventListener( "loadedmetadata", function (e) {
//        console.log("loaded");

//        var v_width = this.videoWidth;
//        var v_height = this.videoHeight;
//
//        const w_width  = (window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth);
//	    const w_height = (window.innerHeight|| document.documentElement.clientHeight|| document.body.clientHeight);
//
//	    if(w_width > v_width){
//	        console.log("Setting width: " + w_width);
//	        video.setAttribute('width', w_width + "px");
//	    }else if(w_height > v_height){
//	        console.log("Setting height: " + w_height);
//	        video.setAttribute('height', w_height + "px");
//	    }else{
//	        console.log("width:" +  v_width  + ", height:" + v_height);
//	    }
//    });
}