// Behaviour for the multi step registration wizard.
//
// htmx does not swap error responses, so a rate limited signup (HTTP 429)
// would fail silently. Show the server's response instead.
//
// The script is also re-executed when the wizard is swapped into the auth
// modal, so guard against registering the listener more than once.
if (!window.__signupWizardInitialised) {
  window.__signupWizardInitialised = true

  document.addEventListener('htmx:responseError', function (event) {
    const xhr = event.detail.xhr
    if (xhr && xhr.status === 429 && xhr.responseText) {
      document.open()
      document.write(xhr.responseText)
      document.close()
    }
  })
}
