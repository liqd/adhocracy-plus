// Behaviour for the multi step registration wizard.
//
// htmx does not swap error responses, so a rate limited signup (HTTP 429)
// would fail silently. Show the server's response instead.
document.addEventListener('htmx:responseError', function (event) {
  const xhr = event.detail.xhr
  if (xhr && xhr.status === 429 && xhr.responseText) {
    document.open()
    document.write(xhr.responseText)
    document.close()
  }
})
