document.addEventListener('DOMContentLoaded', function () {
  const toggleButton = document.getElementById('learning-toggle')
  const sidebar = document.getElementById('learning-sidebar')
  const closeButton = document.getElementById('learning-close')

  toggleButton.classList.add('learning-toggle--js-enabled')

  function setOpen (open) {
    sidebar.classList.toggle('active', open)
    sidebar.setAttribute('aria-hidden', open ? 'false' : 'true')
    toggleButton.setAttribute('aria-expanded', open ? 'true' : 'false')
  }

  // htmx handles loading the content and the URL/history. The toggle only
  // opens the sidebar; the actual request is triggered by its hx-get.
  toggleButton.addEventListener('click', function () {
    setOpen(true)
  })

  closeButton.addEventListener('click', function () {
    setOpen(false)
  })

  // Reflect htmx-driven navigation (back/forward, sidebar links) on the
  // open state.
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
