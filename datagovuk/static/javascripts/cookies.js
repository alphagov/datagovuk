// Common functions to set/unset consent cookie

(function (root) {
  'use strict'
  window.GOVUK = window.GOVUK || {}

  var DEFAULT_COOKIE_CONSENT = {
    essential: true,
    settings: false,
    usage: false,
    campaigns: false
  }

  var COOKIE_CATEGORIES = {
    cookies_policy: 'essential',
    seen_cookie_message: 'essential',
    cookie_preferences_set: 'essential',
    cookies_preferences_set: 'essential',
    '_email-alert-frontend_session': 'essential',
    licensing_session: 'essential',
    govuk_contact_referrer: 'essential',
    multivariatetest_cohort_coronavirus_extremely_vulnerable_rate_limit: 'essential',
    dgu_beta_banner_dismissed: 'settings',
    global_bar_seen: 'settings',
    govuk_browser_upgrade_dismisssed: 'settings',
    govuk_not_first_visit: 'settings',
    analytics_next_page_call: 'usage',
    user_nation: 'settings',
    _ga: 'usage',
    _gid: 'usage',
    _gat: 'usage',
    'JS-Detection': 'usage',
    TLSversion: 'usage'
  }

  /*
    Cookie methods
    ==============

    Usage:

      Setting a cookie:
      GOVUK.cookie('hobnob', 'tasty', { days: 30 });

      Reading a cookie:
      GOVUK.cookie('hobnob');

      Deleting a cookie:
      GOVUK.cookie('hobnob', null);
  */
  window.GOVUK.cookie = function (name, value, options) {
    if (typeof value !== 'undefined') {
      if (value === false || value === null) {
        return window.GOVUK.setCookie(name, '', { days: -1 })
      } else {
        // Default expiry date of 30 days
        if (typeof options === 'undefined') {
          options = { days: 30 }
        }
        return window.GOVUK.setCookie(name, value, options)
      }
    } else {
      return window.GOVUK.getCookie(name)
    }
  }

  window.GOVUK.setDefaultConsentCookie = function () {
    window.GOVUK.setConsentCookie(DEFAULT_COOKIE_CONSENT)
  }

  window.GOVUK.approveAllCookieTypes = function () {
    var approvedConsent = {
      essential: true,
      settings: true,
      usage: true,
      campaigns: true
    }

    window.GOVUK.setCookie('cookies_policy', JSON.stringify(approvedConsent), { days: 365 })
  }

  window.GOVUK.getConsentCookie = function () {
    var consentCookie = window.GOVUK.cookie('cookies_policy')
    var consentCookieObj

    if (consentCookie) {
      try {
        consentCookieObj = JSON.parse(consentCookie)
      } catch (err) {
        return null
      }

      if (typeof consentCookieObj !== 'object' && consentCookieObj !== null) {
        consentCookieObj = JSON.parse(consentCookieObj)
      }
    } else {
      return null
    }

    return consentCookieObj
  }

  window.GOVUK.setConsentCookie = function (options) {
    var cookieConsent = window.GOVUK.getConsentCookie()

    if (!cookieConsent) {
      cookieConsent = JSON.parse(JSON.stringify(DEFAULT_COOKIE_CONSENT))
    }

    for (var cookieType in options) {
      cookieConsent[cookieType] = options[cookieType]

      // Delete cookies of that type if consent being set to false
      if (!options[cookieType]) {
        for (var cookie in COOKIE_CATEGORIES) {
          if (COOKIE_CATEGORIES[cookie] === cookieType) {
            window.GOVUK.deleteCookie(cookie)
          }
        }
      }
    }

    window.GOVUK.setCookie('cookies_policy', JSON.stringify(cookieConsent), { days: 365 })
  }

  window.GOVUK.checkConsentCookieCategory = function (cookieName, cookieCategory) {
    var currentConsentCookie = window.GOVUK.getConsentCookie()

    // If the consent cookie doesn't exist, but the cookie is in our known list, return true
    if (!currentConsentCookie && COOKIE_CATEGORIES[cookieName]) {
      return true
    }

    currentConsentCookie = window.GOVUK.getConsentCookie()

    // Sometimes currentConsentCookie is malformed in some of the tests, so we need to handle these
    try {
      return currentConsentCookie[cookieCategory]
    } catch (e) {
      console.error(e)
      return false
    }
  }

  window.GOVUK.checkConsentCookie = function (cookieName, cookieValue) {
    // If we're setting the consent cookie OR deleting a cookie, allow by default
    if (cookieName === 'cookies_policy' || (cookieValue === null || cookieValue === false)) {
      return true
    }

    // Survey cookies are dynamically generated, so we need to check for these separately
    if (cookieName.match('^govuk_surveySeen') || cookieName.match('^govuk_taken')) {
      return window.GOVUK.checkConsentCookieCategory(cookieName, 'settings')
    }

    if (COOKIE_CATEGORIES[cookieName]) {
      var cookieCategory = COOKIE_CATEGORIES[cookieName]

      return window.GOVUK.checkConsentCookieCategory(cookieName, cookieCategory)
    } else {
      // Deny the cookie if it is not known to us
      return false
    }
  }

  window.GOVUK.setCookie = function (name, value, options) {
    if (window.GOVUK.checkConsentCookie(name, value)) {
      if (typeof options === 'undefined') {
        options = {}
      }
      var cookieString = name + '=' + value + '; path=/'
      if (options.days) {
        var date = new Date()
        date.setTime(date.getTime() + (options.days * 24 * 60 * 60 * 1000))
        cookieString = cookieString + '; expires=' + date.toGMTString()
      }
      if (document.location.protocol === 'https:') {
        cookieString = cookieString + '; Secure'
      }
      document.cookie = cookieString
    }
  }

  window.GOVUK.getCookie = function (name) {
    var nameEQ = name + '='
    var cookies = document.cookie.split(';')
    for (var i = 0, len = cookies.length; i < len; i++) {
      var cookie = cookies[i]
      while (cookie.charAt(0) === ' ') {
        cookie = cookie.substring(1, cookie.length)
      }
      if (cookie.indexOf(nameEQ) === 0) {
        return decodeURIComponent(cookie.substring(nameEQ.length))
      }
    }
    return null
  }

  window.GOVUK.getCookieCategory = function (cookie) {
    return COOKIE_CATEGORIES[cookie]
  }

  window.GOVUK.deleteCookie = function (cookie) {
    window.GOVUK.cookie(cookie, null)

    if (window.GOVUK.cookie(cookie)) {
      // We need to handle deleting cookies on the domain and the .domain
      document.cookie = cookie + '=;expires=' + new Date() + ';'
      document.cookie = cookie + '=;expires=' + new Date() + ';domain=' + window.location.hostname + ';path=/'
    }
  }

  window.GOVUK.deleteUnconsentedCookies = function () {
    var currentConsent = window.GOVUK.getConsentCookie()

    for (var cookieType in currentConsent) {
      // Delete cookies of that type if consent being set to false
      if (!currentConsent[cookieType]) {
        for (var cookie in COOKIE_CATEGORIES) {
          if (COOKIE_CATEGORIES[cookie] === cookieType) {
            window.GOVUK.deleteCookie(cookie)
          }
        }
      }
    }
  }
}(window));

window.GOVUK = window.GOVUK || {}
window.GOVUK.Modules = window.GOVUK.Modules || {};


// Governing cookie banner

(function (Modules) {
  function CookieBanner ($module) {
    this.$module = $module
    this.$module.cookieBanner = document.querySelector('.gem-c-cookie-banner')
    this.$module.cookieBannerConfirmationMessage = this.$module.querySelector('.gem-c-cookie-banner__confirmation')
    this.$module.cookieBannerConfirmationMessageText = this.$module.querySelector('.gem-c-cookie-banner__confirmation-message')
  }

  CookieBanner.prototype.init = function () {
    this.$module.hideCookieMessage = this.hideCookieMessage.bind(this)
    this.$module.showConfirmationMessage = this.showConfirmationMessage.bind(this)
    this.$module.setCookieConsent = this.setCookieConsent.bind(this)
    this.$module.rejectCookieConsent = this.rejectCookieConsent.bind(this)
    this.setupCookieMessage()
  }

  CookieBanner.prototype.setupCookieMessage = function () {
    this.$hideLinks = this.$module.querySelectorAll('button[data-hide-cookie-banner]')
    if (this.$hideLinks && this.$hideLinks.length) {
      for (var i = 0; i < this.$hideLinks.length; i++) {
        this.$hideLinks[i].addEventListener('click', this.$module.hideCookieMessage)
      }
    }

    this.$acceptCookiesButton = this.$module.querySelector('button[data-accept-cookies]')
    if (this.$acceptCookiesButton) {
      this.$acceptCookiesButton.style.display = 'block'
      this.$acceptCookiesButton.addEventListener('click', this.$module.setCookieConsent)
    }

    this.$rejectCookiesButton = this.$module.querySelector('button[data-reject-cookies]')
    if (this.$rejectCookiesButton) {
      this.$rejectCookiesButton.style.display = 'block'
      this.$rejectCookiesButton.addEventListener('click', this.$module.rejectCookieConsent)
    }

    this.showCookieMessage()
  }

  CookieBanner.prototype.showCookieMessage = function () {
    // Show the cookie banner if not in the cookie settings page or in an iframe
    if (!this.isInCookiesPage() && !this.isInIframe()) {
      var shouldHaveCookieMessage = (this.$module && window.GOVUK.cookie('cookies_preferences_set') !== 'true')

      if (shouldHaveCookieMessage) {
        this.$module.style.display = 'block'

        // Set the default consent cookie if it isn't already present
        if (!window.GOVUK.cookie('cookies_policy')) {
          window.GOVUK.setDefaultConsentCookie()
        }

        window.GOVUK.deleteUnconsentedCookies()
      } else {
        this.$module.style.display = 'none'
      }
    } else {
      this.$module.style.display = 'none'
    }
  }

  CookieBanner.prototype.hideCookieMessage = function (event) {
    if (this.$module) {
      this.$module.hidden = true
      this.$module.style.display = 'none'
      window.GOVUK.cookie('cookies_preferences_set', 'true', { days: 365 })
    }

    if (event.target) {
      event.preventDefault()
    }
  }

  CookieBanner.prototype.setCookieConsent = function () {
    if (this.$acceptCookiesButton.getAttribute('data-cookie-types') === 'all') {
      this.$module.cookieBannerConfirmationMessageText.insertAdjacentHTML('afterbegin', 'You have accepted additional cookies. ')
    }
    window.GOVUK.approveAllCookieTypes()
    this.$module.showConfirmationMessage()
    this.$module.cookieBannerConfirmationMessage.focus()
    window.GOVUK.cookie('cookies_preferences_set', 'true', { days: 365 })
    if (window.GOVUK.analyticsInit) {
      window.GOVUK.analyticsInit()
    }
    if (window.GOVUK.globalBarInit) {
      window.GOVUK.globalBarInit.init()
    }
    window.GOVUK.triggerEvent(window, 'cookie-consent')
  }

  CookieBanner.prototype.rejectCookieConsent = function () {
    this.$module.cookieBannerConfirmationMessageText.insertAdjacentHTML('afterbegin', 'You have rejected additional cookies. ')
    this.$module.showConfirmationMessage()
    this.$module.cookieBannerConfirmationMessage.focus()
    window.GOVUK.cookie('cookies_preferences_set', 'true', { days: 365 })
    window.GOVUK.setDefaultConsentCookie()
  }

  CookieBanner.prototype.showConfirmationMessage = function () {
    this.$cookieBannerMainContent = document.querySelector('.js-banner-wrapper')

    this.$cookieBannerMainContent.hidden = true
    this.$module.cookieBannerConfirmationMessage.style.display = 'block'
    this.$module.cookieBannerConfirmationMessage.hidden = false
  }

  CookieBanner.prototype.isInCookiesPage = function () {
    return window.location.pathname === '/help/cookies'
  }

  CookieBanner.prototype.isInIframe = function () {
    return window.parent && window.location !== window.parent.location
  }

  Modules.CookieBanner = CookieBanner
})(window.GOVUK.Modules)

new GOVUK.Modules.CookieBanner(document.querySelector("div#global-cookie-message")).init();

// Governing cookie form

(function (Module) {
  function CookieSettings ($module) {
    this.$module = $module

    this.$module.submitSettingsForm = this.submitSettingsForm.bind(this)

    document.querySelector('form[data-module=cookie-settings]')
      .addEventListener('submit', this.$module.submitSettingsForm)
  }

  CookieSettings.prototype.init = function () {

    this.setInitialFormValues()
  }

  CookieSettings.prototype.setInitialFormValues = function () {
    if (!window.GOVUK.cookie('cookies_policy')) {
      window.GOVUK.setDefaultConsentCookie()
    }

    var currentConsentCookie = window.GOVUK.cookie('cookies_policy')
    var currentConsentCookieJSON = JSON.parse(currentConsentCookie)

    // We don't need the essential value as this cannot be changed by the user
    delete currentConsentCookieJSON["essential"]

    for (var cookieType in currentConsentCookieJSON) {
      var radioButton

      if (currentConsentCookieJSON[cookieType]) {
        radioButton = document.querySelector('input[name=cookies-' + cookieType + '][value=on]')
      } else {
        radioButton = document.querySelector('input[name=cookies-' + cookieType + '][value=off]')
      }

      radioButton.checked = true
    }
  }

  CookieSettings.prototype.submitSettingsForm = function (event) {
    event.preventDefault()

    var formInputs = event.target.getElementsByTagName("input")
    var options = {}

    for ( var i = 0; i < formInputs.length; i++ ) {
      var input = formInputs[i]
      if (input.checked) {
        var name = input.name.replace('cookies-', '')
        var value = input.value === "on" ? true : false

        options[name] = value
      }
    }

    window.GOVUK.setConsentCookie(options)
    window.GOVUK.setCookie('cookies_preferences_set', true, { days: 365 });

    this.showConfirmationMessage()

    if (window.GOVUK.analyticsInit) {
      window.GOVUK.analyticsInit()
    }

    return false
  }

  CookieSettings.prototype.showConfirmationMessage = function () {
    var confirmationMessage = document.querySelector('div[data-cookie-confirmation]')
    var previousPageLink = document.querySelector('.cookie-settings__prev-page')
    var referrer = CookieSettings.prototype.getReferrerLink()

    document.body.scrollTop = document.documentElement.scrollTop = 0

    if (referrer && referrer !== document.location.pathname) {
      previousPageLink.href = referrer
      previousPageLink.style.display = "inline"
    } else {
      previousPageLink.style.display = "none"
    }

    confirmationMessage.style.display = "block"
  }

  CookieSettings.prototype.getReferrerLink = function () {
    return document.referrer ? new URL(document.referrer).pathname : false
  }

  Module.CookieSettings = CookieSettings
})(window.GOVUK.Modules)

var form = document.querySelector("form[data-module='cookie-settings']");
if (form) {
  new GOVUK.Modules.CookieSettings(form).init();
}
