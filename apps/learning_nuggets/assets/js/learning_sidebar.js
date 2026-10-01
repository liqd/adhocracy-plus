document.addEventListener('DOMContentLoaded', function () {
  const toggleButton = document.getElementById('learning-toggle')
  const sidebar = document.getElementById('learning-sidebar')
  const closeButton = document.getElementById('learning-close')
  const sidebarContent = document.getElementById('learning-content')
  const currentPath = window.location.pathname

  toggleButton.classList.add('learning-toggle--js-enabled')

  toggleButton.setAttribute('aria-expanded', 'false')
  sidebar.setAttribute('aria-hidden', 'true')
  sidebar.setAttribute('aria-labelledby', 'learning-toggle')

  // Check URL on page load
  const urlParams = new URLSearchParams(window.location.search)
  const sidebarParam = urlParams.get('sidebar')

  // Load content into sidebar via AJAX
  function loadContent (url) {
    // Always fetch from root, regardless of current page
    const rootRelativeUrl = url.startsWith('/') ? url : `/${url}`

    fetch(rootRelativeUrl, {
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
      .then(response => response.text())
      .then(html => {
        sidebarContent.innerHTML = html

        // Update URL with current path and sidebar parameter
        const newUrl = `${currentPath}?sidebar=${rootRelativeUrl.replace(/^\//, '')}`
        window.history.pushState({ sidebarUrl: rootRelativeUrl }, '', newUrl)
        return html
      })
      .catch(error => {
        console.error('Error loading content:', error)
        sidebarContent.innerHTML = '<p>Failed to load content. Please try again.</p>'
      })
  }

  // Open sidebar
  function openSidebar (url) {
    sidebar.classList.add('active')
    sidebar.setAttribute('aria-hidden', 'false')
    toggleButton.setAttribute('aria-expanded', 'true')

    // Load content if URL is provided
    if (url) {
      loadContent(url)
    } else if (!sidebarContent.innerHTML.trim()) {
      loadContent('/learning-center/')
    }
  }

  // Close sidebar without touching the history stack
  function hideSidebar () {
    sidebar.classList.remove('active')
    sidebar.setAttribute('aria-hidden', 'true')
    toggleButton.setAttribute('aria-expanded', 'false')
  }

  // Close sidebar and remove the sidebar parameter from the URL.
  // Uses replaceState so closing does not push a new history entry.
  function closeSidebar () {
    hideSidebar()
    const url = new URL(window.location.href)
    if (url.searchParams.has('sidebar')) {
      url.searchParams.delete('sidebar')
      window.history.replaceState({}, '', url.pathname + url.search)
    }
  }

  // Toggle sidebar
  toggleButton.addEventListener('click', function (e) {
    e.preventDefault()
    const isSidebarActive = sidebar.classList.contains('active')

    if (isSidebarActive) {
      closeSidebar()
    } else {
      openSidebar()
    }
  })

  // Close sidebar and reset URL
  closeButton.addEventListener('click', function (e) {
    e.preventDefault()
    closeSidebar()
  })

  // Handle clicks inside the sidebar content
  sidebarContent.addEventListener('click', function (e) {
    const link = e.target.closest('a[data-sidebar]')
    if (link) {
      e.preventDefault()
      const url = link.getAttribute('href')
      loadContent(url)
    }
  })

  // Handle browser back/forward buttons
  window.addEventListener('popstate', function (event) {
    const sidebarUrl = event.state && event.state.sidebarUrl
    if (sidebarUrl) {
      openSidebar(sidebarUrl)
    } else {
      hideSidebar()
    }
  })

  // Open sidebar if sidebar parameter exists on page load
  if (sidebarParam) {
    openSidebar(sidebarParam)
  }
})
