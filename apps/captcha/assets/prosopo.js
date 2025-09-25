import { renderProcaptcha } from '@prosopo/procaptcha-wrapper'

document.addEventListener('DOMContentLoaded', function () {
  renderAllCaptchas()

  function renderAllCaptchas () {
    const captchaContainers = document.querySelectorAll('.prosopo-captcha-container')

    captchaContainers.forEach(function (container) {
      const siteKey = container.getAttribute('data-site-key')
      const language = container.getAttribute('data-language') // optional, falls unterstützt
      const hiddenInput = container.previousElementSibling

      if (!siteKey) return

      try {
        container.innerHTML = ''

        renderProcaptcha(container, {
          siteKey,
          language,
          callback: function (token) {
            hiddenInput.value = token
          },
          'expired-callback': function () {
            hiddenInput.value = ''
          },
          'error-callback': function (error) {
            console.error('Prosopo captcha error:', error)
            hiddenInput.value = ''
          }
        })
      } catch (error) {
        console.error('Error initializing Prosopo captcha:', error)
      }
    })
  }
})
