const PARTICIPATION_VIEW_PARAM = 'participation_view'
const PARTICIPATION_VIEW_GRID = 'grid'
const PARTICIPATION_VIEW_TIMELINE = 'timeline'
const VALID_PARTICIPATION_VIEWS = new Set([
  PARTICIPATION_VIEW_GRID,
  PARTICIPATION_VIEW_TIMELINE
])

function getParticipationViewFromUrl () {
  const view = new URL(window.location).searchParams.get(PARTICIPATION_VIEW_PARAM)
  return VALID_PARTICIPATION_VIEWS.has(view) ? view : PARTICIPATION_VIEW_GRID
}

function setParticipationViewInUrl (viewName) {
  const url = new URL(window.location)
  if (viewName === PARTICIPATION_VIEW_GRID) {
    url.searchParams.delete(PARTICIPATION_VIEW_PARAM)
  } else {
    url.searchParams.set(PARTICIPATION_VIEW_PARAM, viewName)
  }
  window.history.pushState({}, '', url)
}

function updateTimelineRail (timeline) {
  if (!timeline || timeline.hidden) {
    return
  }

  const rail = timeline.querySelector('.project-detail__timeline-rail')
  if (!rail) {
    return
  }

  rail.replaceChildren()

  const markers = [...timeline.querySelectorAll('.project-timeline-card__marker')]
  if (markers.length < 2) {
    return
  }

  const timelineRect = timeline.getBoundingClientRect()

  const markerCenterX = (marker) => {
    const rect = marker.getBoundingClientRect()
    return rect.left + rect.width / 2 - timelineRect.left
  }

  for (let i = 0; i < markers.length - 1; i += 1) {
    const startRect = markers[i].getBoundingClientRect()
    const endRect = markers[i + 1].getBoundingClientRect()
    const top = startRect.top + startRect.height / 2 - timelineRect.top
    const height =
      endRect.top + endRect.height / 2 - (startRect.top + startRect.height / 2)

    if (height <= 0) {
      continue
    }

    const segment = document.createElement('span')
    segment.className = 'project-detail__timeline-rail-segment'
    segment.style.top = `${top}px`
    segment.style.height = `${height}px`
    segment.style.left = `${markerCenterX(markers[i])}px`
    rail.appendChild(segment)
  }
}

function initProjectDetailParticipationView () {
  const root = document.querySelector('[data-participation-view]')
  if (!root) {
    return
  }

  const buttons = root.querySelectorAll('[data-participation-view-btn]')
  const panels = root.querySelectorAll('[data-participation-view-panel]')
  const timelinePanel = root.querySelector('[data-participation-view-panel="timeline"]')
  if (!buttons.length || !panels.length) {
    return
  }

  const showView = (viewName, { updateUrl = false } = {}) => {
    buttons.forEach((button) => {
      const isActive = button.dataset.participationViewBtn === viewName
      button.classList.toggle('project-detail__view-btn--active', isActive)
      button.setAttribute('aria-pressed', isActive ? 'true' : 'false')
    })

    panels.forEach((panel) => {
      const isActive = panel.dataset.participationViewPanel === viewName
      panel.toggleAttribute('hidden', !isActive)
    })

    if (updateUrl) {
      setParticipationViewInUrl(viewName)
    }

    if (viewName === PARTICIPATION_VIEW_TIMELINE) {
      requestAnimationFrame(() => updateTimelineRail(timelinePanel))
    }
  }

  buttons.forEach((button) => {
    button.addEventListener('click', (event) => {
      event.preventDefault()
      const viewName = button.dataset.participationViewBtn
      showView(viewName, { updateUrl: true })
    })
  })

  if (timelinePanel) {
    window.addEventListener('resize', () => updateTimelineRail(timelinePanel))
    if (typeof ResizeObserver !== 'undefined') {
      const observer = new ResizeObserver(() => updateTimelineRail(timelinePanel))
      observer.observe(timelinePanel)
    }
  }

  showView(getParticipationViewFromUrl())
}

export { initProjectDetailParticipationView, updateTimelineRail }
