const SIDEBAR_PATH_PATTERN = /^\/learning-center(\/|$)/

// Only same-origin Learning Center paths may be loaded into the overlay. This
// rejects protocol-relative URLs (e.g. //evil.example) that would otherwise be
// fetched cross-origin and injected into the DOM.
function normaliseSidebarUrl (param) {
  if (!param) {
    return null
  }
  const path = param.startsWith('/') ? param : `/${param}`
  if (!SIDEBAR_PATH_PATTERN.test(path)) {
    return null
  }
  return path
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
      // Abort an in-flight search so its response cannot reopen the sidebar.
      const form = document.getElementById('learning-search-form')
      if (form && window.htmx) {
        window.htmx.trigger(form, 'htmx:abort')
      }
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

    // A late search response must not reopen a sidebar the user just closed.
    const requestElement = evt.detail.elt
    const isSearchRequest = requestElement && (
      requestElement.id === 'learning-search-form' ||
      (requestElement.closest && requestElement.closest('#learning-search-form'))
    )
    if (isSearchRequest && !sidebar.classList.contains('active')) {
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
