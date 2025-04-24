function resizeVideo() {
    const videoContainer = document.getElementById('video_container');
    const videoImage = videoContainer.querySelector('img');
    const windowWidth = window.innerWidth;
    const windowHeight = window.innerHeight - 50;

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


// Call resizeVideo on page load
window.addEventListener('load', resizeVideo);

// Call resizeVideo on window resize
window.addEventListener('resize', resizeVideo);

document.addEventListener('DOMContentLoaded', function() {
  const resolutionDropdown = document.getElementById('resolution');

  if (resolutionDropdown) {
    resolutionDropdown.addEventListener('change', function() {
      const selectedResolution = this.value;
      // Construct the new URL with the resolution as a GET parameter
      const newURL = window.location.pathname + '?resolution=' + selectedResolution;
      // Reload the page with the new URL
      window.location.href = newURL;
    });
  }
});