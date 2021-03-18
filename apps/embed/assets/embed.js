/* This code is used to replace the html from a
different page with the html from the current page.
This is how it works:
1) embed.html is delivered to client
2) js reads the url from the body-tag attribute 'data-url'
3) js loads the data from the url in step 2
4) js retrieves all elements from inside the main tags from the loaded html from step3
5) js puts the data from step 4 into the dom from step 1
If a link is clicked, it is also handled by js
6) js checks if the achor tag has an embedTarget-attribute
7) if not the restart from step 2
6) if attribute is set to external, redirect to platform
7) if login is required for next step, login opens in popover
*/

/* global django */

// if this was opened from an embed for login, notify it about success
if (window.opener) {
  window.opener.postMessage(
    JSON.stringify({ name: 'popup-close' }),
    location.origin
  )
}

$(document).ready(function () {
  const $main = $('main')
  let currentPath
  let popup
  const patternsForPopup = /\/accounts\b/
  const $top = $('<div tabindex="-1">')

  // FIXME: use consistent wording (URL/href/path)
  window.adhocracy4.getCurrentPath = function () {
    // currentPath is currently broken - it will result in not closing
    // the login popup. Using login_success will make us close the popup
    // and return to the initial page. This is not correct, but better
    // and consistent with the login button on the embed frame.
    // return currentPath
    return '/embed/login_success'
  }

  const headers = {
    'X-Embed': ''
  }

  const testCanSetCookie = function () {
    document.cookie = 'can-set-cookie=true;SameSite=None;Secure'
    return document.cookie.indexOf('can-set-cookie=') !== -1
  }

  const createAlert = function (text, state, timeout) {
    const $alert = $('<p class="alert alert--' + state + ' alert--small" role="alert">' + text + '</p>')
    const $close = $('<button class="alert__close"><i class="fa fa-times"></i></button>')

    $alert.append($close)
    $close.attr('title', django.gettext('Close'))
    $close.find('i').attr('aria-label', django.gettext('Close'))

    const removeMessage = function () {
      $alert.remove()
    }
    $alert.on('click', removeMessage)
    if (typeof timeout === 'number') {
      setTimeout(removeMessage, timeout)
    }
    $alert.prependTo($('#embed-status'))
  }

  const extractScripts = function ($root, selector, attr) {
    const $existingValues = $('head').find(selector).map((i, e) => $(e).attr(attr))

    $root.find(selector).each(function (i, script) {
      const $script = $(script)
      if ($existingValues.filter((i, v) => v === $script.attr(attr)).length) {
        $script.remove()
      } else {
        $('head').append($script)
      }
    })
  }

  const loadHtml = function (html, textStatus, xhr) {
    const $root = $('<div>').html(html)
    const nextPath = xhr.getResponseHeader('x-ajax-path')

    if (patternsForPopup.test(nextPath)) {
      $('#embed-confirm').modal('show')
      return false
    }
    // only update the currentPath if there was no modal opened
    currentPath = nextPath

    extractScripts($root, 'script[src]', 'src')
    extractScripts($root, 'link[rel="stylesheet"]', 'href')

    $main.empty()
    $main.append($top)
    $main.append($root.find('main').children())

    document.dispatchEvent(new Event('a4.embed.ready'))

    // jump to top after navigation
    $top.focus()
  }

  const onAjaxError = function (jqxhr) {
    let text
    switch (jqxhr.status) {
      case 404:
        text = django.gettext('We couldn\'t find what you were looking for.')
        break
      case 401:
      case 403:
        text = django.gettext('You don\'t have the permission to view this page.')
        break
      default:
        text = django.gettext('Something went wrong!')
        break
    }

    createAlert(text, 'danger', 6000)
  }

  const getEmbedTarget = function ($element, url) {
    const embedTarget = $element.data('embedTarget')

    if (embedTarget) {
      return embedTarget
    } else if (!url || url[0] === '#' || $element.attr('target')) {
      return 'ignore'
    } else if ($element.is('.rich-text a')) {
      return 'external'
    } else if (patternsForPopup.test(url)) {
      return 'popup'
    } else {
      return 'internal'
    }
  }

  $(document).on('click', 'a[href]', function (event) {
    // NOTE: event.target.href is resolved against /embed/
    let url = event.currentTarget.getAttribute('href')
    const $link = $(event.target)
    const embedTarget = getEmbedTarget($link, url)

    if (embedTarget === 'internal') {
      event.preventDefault()

      if (url[0] === '?') {
        url = currentPath + url
      }

      $.ajax({
        url: url,
        headers: headers,
        success: loadHtml,
        error: onAjaxError
      })
    } else if (embedTarget === 'popup') {
      event.preventDefault()
      popup = window.open(
        url,
        'embed_popup',
        'height=650,width=500,location=yes,menubar=no,toolbar=no,status=no'
      )
    }
  })

  $(document).on('submit', 'form[action]', function (event) {
    const form = event.target
    const $form = $(form)
    const embedTarget = getEmbedTarget($form, form.method)

    if (embedTarget === 'internal') {
      event.preventDefault()

      $.ajax({
        url: form.action,
        method: form.method,
        headers: headers,
        data: $form.serialize(),
        success: loadHtml,
        error: onAjaxError
      })
    }
  })

  $('.js-embed-logout').on('click', function (e) {
    e.preventDefault()
    $.post(
      '/accounts/logout/',
      { csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val() },
      function () {
        location.reload()
      }
    )
  })

  // The popup will send a message when the user is logged in. Only after
  // this message the Popup will close.
  window.addEventListener('message', function (e) {
    if (e.origin === location.origin) {
      // Browser extensions might use onmessage too, so catch any exceptions
      try {
        const data = JSON.parse(e.data)

        if (data.name === 'popup-close' && popup) {
          popup.close()
          location.reload()
        }
      } catch (e) {
      }
    }
  }, false)

  if (testCanSetCookie() === false) {
    const text = django.gettext('You have third party cookies disabled. You can still view the content of this project but won\'t be able to login.')
    createAlert(text, 'info')
  }

  $.ajax({
    url: $('body').data('url'),
    headers: headers,
    success: loadHtml,
    error: onAjaxError
  })
})
