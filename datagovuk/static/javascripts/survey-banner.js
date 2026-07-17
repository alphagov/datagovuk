(function () {
  const banner = document.querySelector('[data-module="survey-banner"]');
  if (!banner) return;

  const closeLink = banner.querySelector('.datagovuk-close');
  if (!closeLink) return;

  if (document.cookie.includes('survey-banner-dismissed=true')) {
    banner.hidden = true;
  }

  closeLink.addEventListener('click', function (event) {
    event.preventDefault();
    banner.hidden = true;

    // Set cookie to expire in 30 days
    document.cookie = "survey-banner-dismissed=true; max-age=2592000; path=/; SameSite=Strict";
  });
})();
