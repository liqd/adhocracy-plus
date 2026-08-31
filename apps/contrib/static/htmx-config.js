;(function () {
  'use strict'

  htmx.config.defaultSwapStyle = 'outerHTML'
  htmx.config.globalViewTransitions = false

  document.body.addEventListener('htmx:beforeRequest', function (evt) {
    var csrfToken = document.cookie
      .split('; ')
      .find(function (row) { return row.startsWith('csrftoken=') })
      ?.split('=')[1]
    if (csrfToken) {
      evt.detail.requestConfig.headers['X-CSRFToken'] = csrfToken
    }
  })

  document.body.addEventListener('htmx:afterOnLoad', function (evt) {
    if (evt.detail.xhr.status === 403) {
      var loginUrl = document.querySelector('meta[name="login-url"]')?.content || '/accounts/login/'
      window.location.href = loginUrl
    }
  })
})()