var socket;

function resizeVideo() {
    const videoContainer = document.getElementById('video_container');
    const videoImage = videoContainer.querySelector('img');
    const windowWidth = window.innerWidth;
    const windowHeight = window.innerHeight - 100;

    const imageNaturalWidth = videoImage.naturalWidth;
    const imageNaturalHeight = videoImage.naturalHeight;
    const aspectRatio = imageNaturalWidth / imageNaturalHeight;

    let videoContainerWidth = windowWidth;
    let videoContainerHeight = windowWidth / aspectRatio;

    if (videoContainerHeight > windowHeight) {
        videoContainerHeight = windowHeight;
        videoContainerWidth = windowHeight * aspectRatio;
    }

    videoContainer.style.width = `${videoContainerWidth}px`;
    videoContainer.style.height = `${videoContainerHeight}px`;

    // Explicitly set iframe dimensions to match container
    videoImage.style.width = '100%';
    videoImage.style.height = '100%';
}

function delayResizeVideo(){
    setTimeout(() => {
        resizeVideo();
    }, 1000);
}

/* Call resizeVideo on page load. The resize happens before the first image arrives and alters the size,
so needs to be triggered after a delay */
window.addEventListener('load', delayResizeVideo);

window.addEventListener('resize', resizeVideo);

document.addEventListener('DOMContentLoaded', function() {
    const resolutionDropdown = document.getElementById('resolution');
    const deviceDropdown = document.getElementById('device');

    if (resolutionDropdown) {
    resolutionDropdown.addEventListener('change', function() {
        const selectedResolution = this.value;
        const newURL = window.location.pathname + '?resolution=' + selectedResolution;
        window.location.href = newURL;
    });
    }

    if (deviceDropdown) {
        deviceDropdown.addEventListener('change', function() {
            const selectedDevice = this.value;
            const newURL = window.location.pathname + '?device=' + selectedDevice;
            window.location.href = newURL;
        });
    }

    const socket = io();

    socket.on("switch", function (msg) {
        msg.forEach((state, index) => {
            const switchElement = document.getElementById(`socket${index + 1}`);
            if (switchElement) {
                switchElement.checked = state;
            }
        });
    });

    socket.emit('get_switch');

    document.querySelectorAll('input[type="checkbox"][id^="socket"]').forEach((element) => {
        element.addEventListener('change', function() {
            const idNumber = parseInt(this.id.replace('socket', '')) - 1;
            const isOn = this.checked;
            socket.emit('set_switch', idNumber, isOn);
        });
    });
});


