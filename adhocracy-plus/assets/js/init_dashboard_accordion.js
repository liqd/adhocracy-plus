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

  const manageCookie = (currentElement) => {
    const currentId = parseInt(currentElement.id.split('--')[1])
    const cookie = Cookies.get(COOKIE_NAME)
    const currentExpanded = !currentElement.classList.contains('collapsed')
    let currentList = []

    if (cookie) {
      currentList = JSON.parse(cookie)
    }

    if (!currentExpanded && !currentList.includes(currentId)) {
      currentList.push(currentId)
      Cookies.set(COOKIE_NAME, JSON.stringify(currentList))
    } else if (currentExpanded && currentList.includes(currentId)) {
      currentList.splice(currentList.indexOf(currentId), 1)
      Cookies.set(COOKIE_NAME, JSON.stringify(currentList))
    }
  }

  if (Cookies.get(COOKIE_NAME) === undefined) {
    Cookies.set(COOKIE_NAME, '[]')
  }

  manageObservers()
}
