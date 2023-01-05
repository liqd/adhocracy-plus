/* This code checks if something has been changed in a form but not submitted.
   If the user wants to leave the the page there will be warning. */

/* global django */

document.addEventListener('DOMContentLoaded', () => {
  let submitted = false
  const changeHandler = event => {
    if (event.target === undefined) {
      return
    } else {
      const target = event.target.id
      if (target.includes('dashboardToggle')) {
        submitted = true
      }
    }
    window.addEventListener('beforeunload', (e) => {
      if (!submitted) {
        // string is ignored on most modern browsers
        const string = django.gettext('If you leave this page changes you made will not be saved.')
        e.preventDefault()
        e.returnValue = string
        return string
      }
    })
  }

  if (window.CKEDITOR) {
    // eslint-disable-next-line no-undef
    CKEDITOR.on('instanceReady', function (e) {
      e.editor.on('change', changeHandler)
    })
  }

  document.addEventListener('change', changeHandler, { once: true })
  document.addEventListener('submit', (e) => {
    if (e.target.getAttribute('ignore-submit') === true) {
      return true
    }
    submitted = true
  })
})
