function reload() {
    var city_name = document.getElementById("city_name").value;
    var address = window.location.protocol + "//" + window.location.hostname + ":" + window.location.port  + window.location.pathname + "?city_name=" + city_name;
    location.href = address;
}

function setupVideoQueue(start_id, end_id){
    var startVideo = document.getElementById(start_id);
    var endVideo = document.getElementById(end_id);

    var duration = (startVideo.duration / startVideo.playbackRate - 2) * 1000;

    startVideo.classList.add('showing');
    startVideo.classList.remove('fading');
    endVideo.classList.add('fading');
    endVideo.classList.remove('showing');

    setTimeout(() => {
        startVideo.classList.remove('showing');
        startVideo.classList.add('fading');
        endVideo.classList.remove('fading');
        endVideo.classList.add('showing');
        endVideo.play();
    }, duration)
}


window.onload = function() {
    // Refresh every half an hour
    setTimeout(reload, 1800000);
}