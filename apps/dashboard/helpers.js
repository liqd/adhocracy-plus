import Cookies from 'js-cookie'

export function initDashboardAccordeon () {
  const cookieName = 'dashboard_projects_closed_accordeons'

  if (Cookies.get(cookieName) === undefined) {
    Cookies.set(cookieName, '[]')
  }

  const accordeonMenus = document.querySelectorAll('div.dashboard-nav__dropdown')

  accordeonMenus.forEach(accordeon => {
    const observer = new MutationObserver((mutations) => {
      manageCookie(mutations[0].target)
    })
    const config = { attributes: true, childList: true, characterData: true }
    observer.observe(accordeon, config)
  })

  const manageCookie = (currentElement) => {
    const currentId = parseInt(currentElement.id.split('--')[1])
    const cookie = Cookies.get(cookieName)
    const currentExpanded = !currentElement.classList.contains('collapsed')
    let currentList = []

    if (cookie) {
      currentList = JSON.parse(cookie)
    }

    if (!currentExpanded && !currentList.includes(currentId)) {
      currentList.push(currentId)
      Cookies.set(cookieName, JSON.stringify(currentList))
    } else if (currentExpanded && currentList.includes(currentId)) {
      currentList.splice(currentList.indexOf(currentId), 1)
      Cookies.set(cookieName, JSON.stringify(currentList))
    }
  }
}
