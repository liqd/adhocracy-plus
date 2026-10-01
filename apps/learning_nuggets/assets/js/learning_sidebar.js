/* eslint-disable no-restricted-syntax */
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

  // Close sidebar
  function closeSidebar () {
    sidebar.classList.remove('active')
    sidebar.setAttribute('aria-hidden', 'true')
    toggleButton.setAttribute('aria-expanded', 'false')
    window.history.pushState(null, '', currentPath)
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
    if (event.state && event.state.sidebarUrl) {
      openSidebar(event.state.sidebarUrl)
    } else {
      closeSidebar()
    }
  })

  // Open sidebar if sidebar parameter exists on page load
  if (sidebarParam) {
    openSidebar(sidebarParam)
  }
})
