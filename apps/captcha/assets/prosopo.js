import { renderProcaptcha } from '@prosopo/procaptcha-wrapper'

function renderAllCaptchas () {
  const captchaContainers = document.querySelectorAll('.prosopo-captcha-container')

  captchaContainers.forEach(function (container) {
    // Skip containers that were already rendered (e.g. by an htmx swap)
    if (container.dataset.prosopoInitialized) {
      return
    }
    container.dataset.prosopoInitialized = 'true'

    const siteKey = container.getAttribute('data-site-key')
    const language = container.getAttribute('data-language') // optional, when supported
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

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', renderAllCaptchas)
} else {
  renderAllCaptchas()
}

// The registration wizard swaps the captcha step in via htmx, so render any
// captcha that appears after the initial page load as well.
document.addEventListener('htmx:afterSwap', renderAllCaptchas)
