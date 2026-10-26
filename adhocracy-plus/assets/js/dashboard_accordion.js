import Cookies from 'js-cookie'

const COOKIE_NAME = 'dashboard_projects_closed_accordions'
const HTML_ATTR = 'aria-expanded'
const HIDDEN_ATTR = 'aria-hidden'
const STATUS_SELECTOR = '[data-dashboard-accordion-status]'
const ADDED_MODULE_PARAM = 'added_module'

const collapseTargetOf = (toggle) => {
  const selector = toggle.dataset.bsTarget
  return selector ? document.querySelector(selector) : null
}

const setExpanded = (toggle, expanded) => {
  toggle.classList.toggle('collapsed', !expanded)
  toggle.setAttribute(HTML_ATTR, String(expanded))
  const target = collapseTargetOf(toggle)
  if (target) {
    target.classList.toggle('show', expanded)
    target.setAttribute(HIDDEN_ATTR, String(!expanded))
  }
}

const isId = (value) => Number.isInteger(value)

const asIds = (value) => (Array.isArray(value) ? value.filter(isId) : [])

// Older dashboard versions stored a flat list of collapsed project ids and a
// buggy server version could append a third element, both are normalized here.
const readCookie = () => {
  try {
    const value = JSON.parse(Cookies.get(COOKIE_NAME) || "null")
    if (!Array.isArray(value)) {
      return [[], []]
    }
    if (value.every(isId)) {
      return [value, []]
    }
    return [asIds(value[0]), asIds(value[1])]
  } catch {
    return [[], []]
  }
}

export function initDashboardAccordion () {
  const accordionMenus = document.querySelectorAll('div.dashboard-nav__dropdown')

  const setCookie = (value) => Cookies.set(COOKIE_NAME, value, { sameSite: 'lax' })

  const manageCookie = (toggle) => {
    if (!toggle.id.includes('--')) {
      return
    }
    const id = parseInt(toggle.id.split('--')[1], 10)
    if (!id) {
      return
    }
    const isProject = toggle.id.startsWith('dashboard-nav__project--')
    const current = readCookie()
    const currentList = current[isProject ? 0 : 1]
    const currentExpanded = toggle.getAttribute(HTML_ATTR) === 'true'

    if (!currentExpanded && !currentList.includes(id)) {
      currentList.push(id)
      setCookie(JSON.stringify(current))
    } else if (currentExpanded && currentList.includes(id)) {
      currentList.splice(currentList.indexOf(id), 1)
      setCookie(JSON.stringify(current))
    }
  }

  const observer = new MutationObserver((mutations) => {
    mutations
      .filter(m => m.attributeName === HTML_ATTR)
      .forEach(m => {
        manageCookie(m.target)
        const target = collapseTargetOf(m.target)
        if (target) {
          target.setAttribute(HIDDEN_ATTR, m.target.getAttribute(HTML_ATTR) === 'true' ? 'false' : 'true')
        }
      })
  })

  accordionMenus.forEach(toggle => {
    observer.observe(toggle, { attributeFilter: [HTML_ATTR] })
    toggle.addEventListener('keydown', (event) => {
      if (event.key !== 'Enter' && event.key !== ' ') {
        return
      }
      event.preventDefault()
      toggle.click()
    })
  })

  if (Cookies.get(COOKIE_NAME) === undefined) {
    setCookie('[[], []]')
  }
}

// After a module was added, collapse the other modules, move the focus to the
// new module and announce the change to screen reader users.
export function initAddedModuleFocus () {
  const url = new URL(window.location.href)
  const moduleId = parseInt(url.searchParams.get(ADDED_MODULE_PARAM), 10)
  if (!moduleId) {
    return
  }

  const accordion = document.getElementById(`dashboard-nav__module--${moduleId}`)
  if (!accordion) {
    return
  }

  document
    .querySelectorAll('div.dashboard-nav__dropdown[id^="dashboard-nav__module--"]')
    .forEach(toggle => {
      if (toggle !== accordion) {
        setExpanded(toggle, false)
      }
    })

  const activeLink = accordion.parentElement.querySelector('.dashboard-nav__item.is-active')
  const target = activeLink || accordion
  target.focus()

  const status = document.querySelector(STATUS_SELECTOR)
  if (status) {
    status.textContent = status.dataset.dashboardAccordionStatus
  }

  url.searchParams.delete(ADDED_MODULE_PARAM)
  window.history.replaceState({}, '', url)
}
