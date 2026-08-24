class DatagovukNotificationBannerClose {
  constructor($module) {
    this.$module = $module
    this.$closeLink = $module.querySelector('.datagovuk-close')

    if (!this.$closeLink) return

    this.$module.focus()
    this.$closeLink.addEventListener('click', (event) => this.dismiss(event))
  }

  dismiss(event) {
    event.preventDefault()
    this.$module.hidden = true
  }
}

document.querySelectorAll('[data-module="notification-banner-close"]').forEach(($el) => {
  new DatagovukNotificationBannerClose($el)
})
