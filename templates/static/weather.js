function reload() {
    location.reload();
}


window.onload = function() {
    // Refresh every half an hour
    setTimeout(reload, 1800000);
}