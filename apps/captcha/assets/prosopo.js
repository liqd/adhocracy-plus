// Prosopo Captcha Integration using explicit rendering
document.addEventListener('DOMContentLoaded', function () {
  // Wait for the procaptcha script to load
  const procaptchaScript = document.getElementById('procaptcha-script')

  if (!procaptchaScript) {
    return
  }

  // Add load event listener to the script tag
  procaptchaScript.addEventListener('load', function () {
    renderAllCaptchas()
  })

  // If script is already loaded, render immediately
  if (procaptchaScript.complete || procaptchaScript.readyState === 'complete') {
    renderAllCaptchas()
  }

  function renderAllCaptchas () {
    const captchaContainers = document.querySelectorAll('.prosopo-captcha-container')

    captchaContainers.forEach(function (container, index) {
      const siteKey = container.getAttribute('data-site-key')
      const language = container.getAttribute('data-language')
      const hiddenInput = container.previousElementSibling

      if (!siteKey || siteKey === '') {
        return
      }

      try {
        // Clear the container and render the captcha
        container.innerHTML = ''

        // Render the CAPTCHA explicitly on the container
        window.procaptcha.render(container, {
          siteKey,
          language,
          callback: function (output) {
            // Extract the token from the output
            if (output && output.token) {
              hiddenInput.value = output.token
            } else {
              hiddenInput.value = output
            }
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
