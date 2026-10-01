document.addEventListener('DOMContentLoaded', function () {
  const toggleButton = document.getElementById('learning-toggle')
  const sidebar = document.getElementById('learning-sidebar')
  const closeButton = document.getElementById('learning-close')
  const backdrop = document.getElementById('learning-sidebar-backdrop')

  if (!sidebar) {
    return
  }

  // Capture the page URL (without any sidebar deep-link param) so it can be
  // restored when the overlay is closed.
  const pageParams = new URLSearchParams(window.location.search)
  pageParams.delete('sidebar')
  const query = pageParams.toString()
  const pageUrl = window.location.pathname + (query ? `?${query}` : '')

  if (toggleButton) {
    toggleButton.classList.add('learning-toggle--js-enabled')
  }

  function setOpen (open) {
    sidebar.classList.toggle('active', open)
    sidebar.setAttribute('aria-hidden', open ? 'false' : 'true')
    if (backdrop) {
      backdrop.classList.toggle('active', open)
    }
    if (toggleButton) {
      toggleButton.setAttribute('aria-expanded', open ? 'true' : 'false')
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
      setOpen(true)
    })
  }

  if (closeButton) {
    closeButton.addEventListener('click', function () {
      setOpen(false)
    })
  }

  // Clicking the dimmed area outside the panel closes the overlay.
  if (backdrop) {
    backdrop.addEventListener('click', function () {
      setOpen(false)
    })
  }

  // Esc closes the overlay and returns focus to the toggle.
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && sidebar.classList.contains('active')) {
      setOpen(false)
      if (toggleButton) {
        toggleButton.focus({ preventScroll: true })
      }
    }
  })

  // Reflect htmx-driven navigation (back/forward, sidebar links) on the open state.
  document.body.addEventListener('htmx:afterSwap', function (evt) {
    if (evt.detail.target && evt.detail.target.id === 'learning-content') {
      setOpen(true)
    }
  })

  // A ?sidebar=<path> deep link opens the sidebar and loads that path via htmx.
  const sidebarParam = new URLSearchParams(window.location.search).get('sidebar')
  if (sidebarParam) {
    setOpen(true)
    const url = sidebarParam.startsWith('/') ? sidebarParam : `/${sidebarParam}`
    window.htmx.ajax('GET', url, {
      target: '#learning-content',
      swap: 'innerHTML'
    })
  }
})
