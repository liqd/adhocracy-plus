function initProjectDetailParticipationView () {
  const root = document.querySelector('[data-participation-view]')
  if (!root) {
    return
  }

  const buttons = root.querySelectorAll('[data-participation-view-btn]')
  const panels = root.querySelectorAll('[data-participation-view-panel]')
  if (!buttons.length || !panels.length) {
    return
  }

  const showView = (viewName) => {
    buttons.forEach((button) => {
      const isActive = button.dataset.participationViewBtn === viewName
      button.classList.toggle('project-detail__view-btn--active', isActive)
      button.setAttribute('aria-pressed', isActive ? 'true' : 'false')
    })

    panels.forEach((panel) => {
      const isActive = panel.dataset.participationViewPanel === viewName
      panel.hidden = !isActive
    })
  }

  buttons.forEach((button) => {
    button.addEventListener('click', () => {
      showView(button.dataset.participationViewBtn)
    })
  })
}

export { initProjectDetailParticipationView }
