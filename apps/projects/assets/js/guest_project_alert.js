const STORAGE_PREFIX = 'a4-guest-alert-dismissed:'

function initGuestProjectAlert (alertEl) {
  const projectSlug = alertEl.dataset.projectSlug
  if (!projectSlug) {
    alertEl.hidden = false
    return
  }

  const storageKey = `${STORAGE_PREFIX}${projectSlug}`
  if (sessionStorage.getItem(storageKey)) {
    alertEl.remove()
    return
  }

  alertEl.hidden = false

  const dismissButton = alertEl.querySelector('[data-guest-alert-dismiss]')
  if (!dismissButton) {
    return
  }

  dismissButton.addEventListener('click', () => {
    sessionStorage.setItem(storageKey, '1')
    alertEl.remove()
  })
}

export function initGuestProjectAlerts () {
  document.querySelectorAll('[data-guest-alert]').forEach(initGuestProjectAlert)
}
