const LEARNING_CENTER_PREFIX = '/learning-center'

// Only same-origin Learning Center paths may be loaded into the overlay. The
// value is parsed and normalised by the browser first, so dot segments
// (e.g. /learning-center/../admin/) cannot escape the prefix and
// protocol-relative URLs (e.g. //evil.example) fail the origin check.
function normaliseSidebarUrl (param) {
  if (!param) {
    return null
  }

  let url
  try {
    url = new URL(param, window.location.origin)
  } catch (error) {
    return null
  }

  if (url.origin !== window.location.origin) {
    return null
  }

  const path = url.pathname
  if (path !== LEARNING_CENTER_PREFIX && !path.startsWith(`${LEARNING_CENTER_PREFIX}/`)) {
    return null
  }

  // A percent-encoded slash or dot may be decoded into a path separator by the
  // server, so only already canonical paths are accepted.
  let decodedPath
  try {
    decodedPath = decodeURIComponent(path)
  } catch (error) {
    return null
  }
  if (decodedPath !== path) {
    return null
  }

  return path + url.search
}

document.addEventListener('DOMContentLoaded', function () {
  const toggleButton = document.getElementById('learning-toggle')
  const sidebar = document.getElementById('learning-sidebar')
  const closeButton = document.getElementById('learning-close')
  const backdrop = document.getElementById('learning-sidebar-backdrop')
  const searchStatus = document.getElementById('learning-search-status')

  if (!sidebar) {
    return
  }

  // Set when the user closes the overlay. A late htmx response must not reopen
  // it, no matter whether it came from the search, the toggle or a link.
  let userClosed = false

  // Requests currently loading sidebar content, so closing the overlay can
  // abort all of them at once.
  const pendingContentRequests = new Set()

  document.body.addEventListener('htmx:beforeRequest', function (evt) {
    const target = evt.detail.target
    if (target && target.id === 'learning-content') {
      pendingContentRequests.add(evt.detail.elt || evt.target)
    }
  })

  document.body.addEventListener('htmx:afterRequest', function (evt) {
    pendingContentRequests.delete(evt.detail.elt || evt.target)
  })

  const FOCUSABLE_SELECTOR = [
    'a[href]',
    'button:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    '[tabindex]:not([tabindex="-1"])'
  ].join(',')

  // The search form lives in the persistent sidebar shell, so its state can be
  // kept in sync with htmx navigation without being replaced by swaps.
  function searchInputElement () {
    return document.getElementById('learning-search-input')
  }

  function searchClearElement () {
    return document.getElementById('learning-search-clear')
  }

  function syncSearchClear () {
    const input = searchInputElement()
    const clear = searchClearElement()
    if (input && clear) {
      clear.hidden = input.value.length === 0
    }
  }

  document.addEventListener('input', function (event) {
    if (event.target && event.target.id === 'learning-search-input') {
      syncSearchClear()
    }
  })

  document.addEventListener('click', function (event) {
    if (!event.target.closest || !event.target.closest('#learning-search-clear')) {
      return
    }
    const input = searchInputElement()
    if (!input) {
      return
    }
    input.value = ''
    syncSearchClear()
    input.focus()
    // Let htmx's `input changed` trigger restore the default sidebar content.
    input.dispatchEvent(new Event('input', { bubbles: true }))
  })

  syncSearchClear()

  // Capture the page URL (without any sidebar deep-link param) so it can be
  // restored when the overlay is closed.
  const pageParams = new URLSearchParams(window.location.search)
  pageParams.delete('sidebar')
  const query = pageParams.toString()
  const pageUrl = window.location.pathname + (query ? `?${query}` : '')

  if (toggleButton) {
    toggleButton.classList.add('learning-toggle--js-enabled')
  }

  function focusableElements () {
    return Array.from(sidebar.querySelectorAll(FOCUSABLE_SELECTOR)).filter(function (el) {
      return el.getClientRects().length > 0
    })
  }

  // `moveFocus` moves keyboard focus into the overlay when it is opened by the
  // user and back to the trigger when it is closed. Programmatic openings
  // (deep link, content loaded via htmx) keep the current focus.
  function setOpen (open, moveFocus) {
    const wasOpen = sidebar.classList.contains('active')
    sidebar.classList.toggle('active', open)
    sidebar.setAttribute('aria-hidden', open ? 'false' : 'true')
    if (backdrop) {
      backdrop.classList.toggle('active', open)
    }
    if (toggleButton) {
      toggleButton.setAttribute('aria-expanded', open ? 'true' : 'false')
    }

    if (!open && wasOpen) {
      // Remember the explicit close and abort every request still loading
      // sidebar content so none of their responses can reopen the overlay.
      userClosed = true
      pendingContentRequests.forEach(function (element) {
        if (window.htmx) {
          window.htmx.trigger(element, 'htmx:abort')
        }
      })
      pendingContentRequests.clear()
    }

    if (open && moveFocus && !wasOpen) {
      const target = closeButton || focusableElements()[0] || sidebar
      target.focus({ preventScroll: true })
    } else if (!open && wasOpen && moveFocus && toggleButton) {
      toggleButton.focus({ preventScroll: true })
    }

    if (!open && window.location.pathname + window.location.search !== pageUrl) {
      // Sidebar navigation may have pushed URLs; restore the underlying page.
      window.history.replaceState({}, '', pageUrl)
    }
  }

  // htmx handles loading the content; the toggle only opens the sidebar and
  // its request is triggered by the button's own hx-get.
  if (toggleButton) {
    toggleButton.addEventListener('click', function () {
      userClosed = false
      setOpen(true, true)
    })
  }

  if (closeButton) {
    closeButton.addEventListener('click', function () {
      setOpen(false, true)
    })
  }

  // Clicking the dimmed area outside the panel closes the overlay.
  if (backdrop) {
    backdrop.addEventListener('click', function () {
      setOpen(false, true)
    })
  }

  // While the overlay is open it behaves as a modal dialog: Esc closes it and
  // Tab is trapped inside the panel.
  document.addEventListener('keydown', function (event) {
    if (!sidebar.classList.contains('active')) {
      return
    }

    if (event.key === 'Escape') {
      event.preventDefault()
      setOpen(false, true)
      return
    }

    if (event.key !== 'Tab') {
      return
    }

    const focusable = focusableElements()
    if (!focusable.length) {
      event.preventDefault()
      return
    }

    const first = focusable[0]
    const last = focusable[focusable.length - 1]
    const active = document.activeElement

    if (event.shiftKey) {
      if (active === first || !sidebar.contains(active)) {
        event.preventDefault()
        last.focus()
      }
    } else if (active === last || !sidebar.contains(active)) {
      event.preventDefault()
      first.focus()
    }
  })

  // Reflect htmx-driven navigation (back/forward, sidebar links) on the open state.
  document.body.addEventListener('htmx:afterSwap', function (evt) {
    if (!evt.detail.target || evt.detail.target.id !== 'learning-content') {
      return
    }

    // A response that arrives after the user closed the overlay must not
    // reopen it (the request was aborted, but a racing response can still
    // arrive).
    if (userClosed) {
      return
    }

    setOpen(true, false)

    const responseUrl = evt.detail.xhr && evt.detail.xhr.responseURL
    if (!responseUrl) {
      return
    }

    const searchQuery = new URL(
      responseUrl,
      window.location.origin
    ).searchParams.get('q')
    const input = searchInputElement()
    if (!input) {
      return
    }

    // Keep the field in sync with the loaded content (e.g. deep links), but
    // never overwrite it while the user is typing.
    if (document.activeElement !== input) {
      input.value = searchQuery || ''
      syncSearchClear()
    }

    if (!searchQuery && searchStatus) {
      searchStatus.textContent = ''
    }
  })

  // A ?sidebar=<path> deep link opens the sidebar and loads that path via htmx.
  const sidebarParam = new URLSearchParams(window.location.search).get('sidebar')
  const sidebarUrl = normaliseSidebarUrl(sidebarParam)
  if (sidebarUrl && window.htmx) {
    setOpen(true, false)
    window.htmx.ajax('GET', sidebarUrl, {
      target: '#learning-content',
      swap: 'innerHTML'
    })
  }
})
