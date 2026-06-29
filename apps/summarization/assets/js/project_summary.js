function getCsrfToken () {
  const name = 'csrftoken'
  const cookies = document.cookie.split(';')
  for (const cookie of cookies) {
    const value = cookie.trim()
    if (value.startsWith(`${name}=`)) {
      return decodeURIComponent(value.substring(name.length + 1))
    }
  }
  return ''
}

function bindSummaryFeedback (root) {
  const feedbackUrl = root.dataset.feedbackUrl
  if (!feedbackUrl) {
    return
  }

  root.querySelectorAll('[data-summary-feedback]').forEach((feedbackRoot) => {
    const summaryId = feedbackRoot.dataset.summaryId
    if (!summaryId) {
      return
    }

    feedbackRoot.querySelectorAll('[data-summary-feedback-value]').forEach((button) => {
      button.addEventListener('click', async () => {
        const feedback = button.dataset.summaryFeedbackValue
        const response = await fetch(feedbackUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
          },
          credentials: 'same-origin',
          body: JSON.stringify({
            summary_id: Number(summaryId),
            feedback
          })
        })

        if (!response.ok) {
          return
        }

        feedbackRoot.querySelectorAll('[data-summary-feedback-value]').forEach((item) => {
          const isActive = item === button
          item.classList.toggle('summary-feedback__btn--active', isActive)
          item.setAttribute('aria-pressed', isActive ? 'true' : 'false')
          const icon = item.querySelector('i')
          if (icon) {
            icon.classList.toggle('fa-solid', isActive)
            icon.classList.toggle('fa-regular', !isActive)
          }
        })
      })
    })
  })
}

function showLoadingState (root) {
  const teaser = root.querySelector('[data-project-summary-teaser]')
  const loading = root.querySelector('[data-project-summary-loading]')
  const error = root.querySelector('[data-project-summary-error]')
  if (teaser) {
    teaser.hidden = true
  }
  if (loading) {
    loading.hidden = false
  }
  if (error) {
    error.hidden = true
    error.textContent = ''
  }
}

function showErrorState (root, message) {
  const teaser = root.querySelector('[data-project-summary-teaser]')
  const loading = root.querySelector('[data-project-summary-loading]')
  const error = root.querySelector('[data-project-summary-error]')
  const generateButton = root.querySelector('[data-project-summary-generate]')

  if (loading) {
    loading.hidden = true
  }
  if (teaser) {
    teaser.hidden = false
  }
  if (error) {
    error.hidden = false
    error.textContent = message
  }
  if (generateButton) {
    generateButton.disabled = false
  }
}

function initProjectSummary () {
  document.querySelectorAll('[data-project-summary]').forEach((root) => {
    const content = root.querySelector('[data-project-summary-content]')
    const summaryUrl = root.dataset.summaryUrl
    if (!content || !summaryUrl) {
      return
    }

    bindSummaryFeedback(root)

    const generateButton = root.querySelector('[data-project-summary-generate]')
    if (generateButton) {
      generateButton.addEventListener('click', async () => {
        showLoadingState(root)
        generateButton.disabled = true

        try {
          const response = await fetch(summaryUrl, {
            method: 'POST',
            headers: {
              'X-CSRFToken': getCsrfToken()
            },
            credentials: 'same-origin'
          })
          let payload = {}
          try {
            payload = await response.json()
          } catch (parseError) {
            payload = {}
          }
          if (!response.ok || !payload.html) {
            throw new Error(payload.error || 'Summary request failed')
          }
          content.innerHTML = payload.html
          bindSummaryFeedback(root)
        } catch (error) {
          showErrorState(
            root,
            error.message || 'Summary generation failed. Please try again later.'
          )
        }
      })
    }
  })
}

export { initProjectSummary }
