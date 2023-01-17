const apiUrl = "http://ujagaga.tplinkdns.com/api/";

var token;
var clr_r;
var clr_g;
var clr_b;
var clr_a;

function getCookie(cname) {
  let name = cname + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(';');
  for(let i = 0; i <ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

function updateSlideColor(){
	var msg = '[' + (clr_r.value * 10) + ',' + (clr_g.value * 10) + ',' + (clr_b.value * 10) + ',' + (clr_a.value * 10) + ']';
    var url = apiUrl + "office_light_set?token=" + token + "&current=" + msg;
    const Http = new XMLHttpRequest();
    Http.open("GET", url, true);
    Http.send();

    Http.onreadystatechange = function(){
      if(this.readyState==4){
        if(this.status!=200){
            console.log("ERROR:" + Http.responseText);
        }
      }
    }
}

function getLightColor(){
    var url = apiUrl + "office_light_get?token=" + token;
    const Http = new XMLHttpRequest();
    Http.open("GET", url, true);
    Http.send();

    Http.onreadystatechange = function(){
      if(this.readyState==4){
        if(this.status==200){
            var data = JSON.parse(Http.responseText);
            if(data.hasOwnProperty('Detail')){
                if(data.Detail.hasOwnProperty('CURRENT')){
                    var current = data.Detail.CURRENT;
                    clr_r.value = parseInt(current[0]) / 10;
                    clr_g.value = parseInt(current[1]) / 10;
                    clr_b.value = parseInt(current[2]) / 10;
                    clr_a.value = parseInt(current[3]) / 10;
                }else{
                    console.log("ERROR parsing Detail JSON:" + data.Detail);
                }
            }else{
                console.log("ERROR parsing JSON:" + Http.responseText);
            }
        }else{
            console.log("ERROR:" + Http.responseText);
        }
      }
    }
}

window.onload = function() {
    var stream_user = document.getElementById('stream_user').value;
    var stream_pass = document.getElementById('stream_pwd').value;
    var printer_link = document.getElementById('printer_url');
    printer_link.href = window.location.protocol + "//" + stream_user + ":" + stream_pass + "@" +
    window.location.hostname + ":8013";

    token = getCookie("token");

    /* Add slider events */
    clr_r = document.getElementById('c_r');
    clr_g = document.getElementById('c_g');
    clr_b = document.getElementById('c_b');
    clr_a = document.getElementById('c_a');

    clr_r.addEventListener('change', function(e){
	    updateSlideColor();
    });
    clr_g.addEventListener('change', function(e){
        updateSlideColor();
    });
    clr_b.addEventListener('change', function(e){
        updateSlideColor();
    });
    clr_a.addEventListener('change', function(e){
        updateSlideColor();
    });

    getLightColor();

}

