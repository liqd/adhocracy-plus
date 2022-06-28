import Cookies from 'js-cookie'

document.addEventListener('DOMContentLoaded', initDashboardAccordion, false)
document.removeEventListener('unload', initDashboardAccordion)

function initDashboardAccordion () {
  const COOKIE_NAME = 'dashboard_projects_closed_accordions'
  const HTML_ATTR = 'aria-expanded'
  const accordionMenus = document.querySelectorAll('div.dashboard-nav__dropdown')

  const manageObservers = () => {
    const observer = new MutationObserver((mutations) => {
      const foundMutation = mutations.find(m => m.attributeName === HTML_ATTR)
      manageCookie(foundMutation.target)
    })

    accordionMenus.forEach(accordion => {
      const config = { attributeFilter: [HTML_ATTR] }
      observer.observe(accordion, config)
    })
  }

  const setCookie = (value) => Cookies.set(COOKIE_NAME, value, { sameSite: 'lax' })

  const manageCookie = (currentElement) => {
    const currentId = parseInt(currentElement.id.split('--')[1])
    const isProject = currentElement.id.startsWith('dashboard-nav__project--')
    const cookie = Cookies.get(COOKIE_NAME)
    const currentExpanded = !currentElement.classList.contains('collapsed')
    let current = [[], []]
    let currentList = []

    if (cookie) {
      current = JSON.parse(cookie)
    }
    currentList = current[isProject ? 0 : 1]
    if (!currentExpanded && !currentList.includes(currentId)) {
      currentList.push(currentId)
      setCookie(JSON.stringify(current))
    } else if (currentExpanded && currentList.includes(currentId)) {
      currentList.splice(currentList.indexOf(currentId), 1)
      setCookie(JSON.stringify(current))
    }
  }

  if (Cookies.get(COOKIE_NAME) === undefined) {
    setCookie('[[], []]')
  }

  manageObservers()
}
