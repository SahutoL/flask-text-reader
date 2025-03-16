if ("serviceWorker" in navigator) {
  navigator.serviceWorker
    .register("/static/js/service-worker.js")
    .then(function (registration) {
      console.log("Service Worker registered with scope:", registration.scope);
      registration.onupdatefound = function () {
        const installingWorker = registration.installing;
        installingWorker.onstatechange = function () {
          if (installingWorker.state === "installed") {
            if (navigator.serviceWorker.controller) {
              console.log("New content is available; please refresh.");
              navigator.serviceWorker.addEventListener(
                "controllerchange",
                function () {
                  window.location.reload();
                }
              );
            } else {
              console.log("Content is cached for offline use.");
            }
          }
        };
      };
    })
    .catch(function (error) {
      console.log("Service Worker registration failed:", error);
    });
  navigator.serviceWorker.addEventListener("controllerchange", function () {
    console.log("Controller change detected. Reloading page.");
    window.location.reload();
  });
}
