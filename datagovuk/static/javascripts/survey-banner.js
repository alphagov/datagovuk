(function () {
  const banner = document.querySelector('[data-module="survey-banner"]');
  if (!banner) return;

  const closeLink = banner.querySelector('.datagovuk-close');
  if (!closeLink) return;

  if (window.sessionStorage.getItem('survey-banner-dismissed') === 'true') {
    banner.hidden = true;
  }

  closeLink.addEventListener('click', function (event) {
    event.preventDefault();
    banner.hidden = true;
    window.sessionStorage.setItem('survey-banner-dismissed', 'true');
  });
})();
