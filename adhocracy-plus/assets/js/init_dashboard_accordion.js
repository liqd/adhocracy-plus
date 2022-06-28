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
    const cookie = Cookies.get(COOKIE_NAME)
    const currentExpanded = !currentElement.classList.contains('collapsed')
    let currentList = []

    if (cookie) {
      currentList = JSON.parse(cookie)
    }

    if (!currentExpanded && !currentList.includes(currentId)) {
      currentList.push(currentId)
      setCookie(JSON.stringify(currentList))
    } else if (currentExpanded && currentList.includes(currentId)) {
      currentList.splice(currentList.indexOf(currentId), 1)
      setCookie(JSON.stringify(currentList))
    }
  }

  if (Cookies.get(COOKIE_NAME) === undefined) {
    setCookie('[]')
  }

  manageObservers()
}
