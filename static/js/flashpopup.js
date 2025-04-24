document.addEventListener("DOMContentLoaded", function () {
  const flashMessageOverlay = document.querySelector(".flash-message-overlay");
  if (flashMessageOverlay) {
    flashMessageOverlay.addEventListener("click", function () {
      flashMessageOverlay.style.display = "none";
    });
    setTimeout(function () {
      flashMessageOverlay.style.display = "none";
    }, 5000);
  }
});
