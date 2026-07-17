class DatagovukSurveyBanner {
  constructor($module) {
    this.$module = $module
    this.$closeLink = $module.querySelector('.datagovuk-close')

    if (!this.$closeLink) return

    if (window.GOVUK.getCookie('survey_banner_dismissed') === 'true') {
      this.$module.hidden = true
      return
    }

    this.$closeLink.addEventListener('click', (event) => this.dismiss(event))
  }

  dismiss(event) {
    event.preventDefault()
    this.$module.hidden = true
    window.GOVUK.cookie('survey_banner_dismissed', 'true', { days: 30 })
  }
}

// Initialize
const $surveyBanner = document.querySelector('.datagovuk-notification-banner')
if ($surveyBanner) {
  new DatagovukSurveyBanner($surveyBanner)
}
