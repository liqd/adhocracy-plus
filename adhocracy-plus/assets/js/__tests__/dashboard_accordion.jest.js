import Cookies from 'js-cookie'

import { initAddedModuleFocus, initDashboardAccordion } from '../dashboard_accordion.js'

const COOKIE_NAME = 'dashboard_projects_closed_accordions'

const accordionMarkup = `
  <nav>
    <div class="visually-hidden" role="status" data-dashboard-accordion-status="MSG"></div>
    <div class="dashboard-nav">
      <div class="dashboard-nav__dropdown" id="dashboard-nav__project--7" aria-expanded="true" data-bs-target="#dashboardCollapseProj"></div>
      <ul id="dashboardCollapseProj" class="show"></ul>
    </div>
    <div class="dashboard-nav">
      <div class="dashboard-nav__dropdown" id="dashboard-nav__module--2" aria-expanded="true" data-bs-target="#dashboardCollapse_1"></div>
      <ul id="dashboardCollapse_1" class="show">
        <li><a class="dashboard-nav__item is-active" href="#">Basic</a></li>
      </ul>
    </div>
    <div class="dashboard-nav">
      <div class="dashboard-nav__dropdown" id="dashboard-nav__module--4" aria-expanded="true" data-bs-target="#dashboardCollapse_2"></div>
      <ul id="dashboardCollapse_2" class="show"></ul>
    </div>
  </nav>`

const moduleWithoutActivePageMarkup = `
  <nav>
    <div class="dashboard-nav">
      <div class="dashboard-nav__dropdown" id="dashboard-nav__module--3" tabindex="0" aria-expanded="true" data-bs-target="#dashboardCollapse_3"></div>
      <ul id="dashboardCollapse_3" class="show">
        <li><a class="dashboard-nav__item" href="#">Basic</a></li>
      </ul>
    </div>
  </nav>`

const nextTick = () => new Promise(resolve => setTimeout(resolve, 0))

const collapse = async (element) => {
  element.classList.add('collapsed')
  element.setAttribute('aria-expanded', 'false')
  await nextTick()
}

describe('dashboard accordion', () => {
  beforeEach(() => {
    document.body.innerHTML = accordionMarkup
    Cookies.remove(COOKIE_NAME)
  })

  it('collapses the other modules and focuses the added one', async () => {
    initDashboardAccordion()
    window.history.replaceState({}, '', '/dashboard?added_module=2')

    initAddedModuleFocus()
    await nextTick()

    const added = document.getElementById('dashboard-nav__module--2')
    const other = document.getElementById('dashboard-nav__module--4')
    const project = document.getElementById('dashboard-nav__project--7')
    expect(added.getAttribute('aria-expanded')).toBe('true')
    expect(other.getAttribute('aria-expanded')).toBe('false')
    expect(document.getElementById('dashboardCollapse_2').classList.contains('show')).toBe(false)
    expect(document.getElementById('dashboardCollapse_2').getAttribute('aria-hidden')).toBe('true')
    expect(project.getAttribute('aria-expanded')).toBe('true')
    expect(document.activeElement.textContent).toBe('Basic')
    expect(document.querySelector('[role="status"]').textContent).toBe('MSG')
    expect(JSON.parse(Cookies.get(COOKIE_NAME))).toEqual([[], [4]])
    expect(window.location.search).toBe('')
  })

  it('focuses the module header if no page is active', () => {
    document.body.innerHTML = moduleWithoutActivePageMarkup
    window.history.replaceState({}, '', '/dashboard?added_module=3')

    initAddedModuleFocus()

    const header = document.getElementById('dashboard-nav__module--3')
    expect(document.activeElement).toBe(header)
    expect(header.getAttribute('tabindex')).toBe('0')
  })

  it('ignores the focus handling without an added module', () => {
    window.history.replaceState({}, '', '/dashboard')

    initAddedModuleFocus()

    expect(document.activeElement).toBe(document.body)
  })

  it('syncs aria-hidden when an accordion is toggled', async () => {
    initDashboardAccordion()
    const toggle = document.getElementById('dashboard-nav__module--2')
    const pages = document.getElementById('dashboardCollapse_1')

    await collapse(toggle)

    expect(pages.getAttribute('aria-hidden')).toBe('true')
    expect(JSON.parse(Cookies.get(COOKIE_NAME))).toEqual([[], [2]])
  })

  it('stores collapsed project sections in the project slot', async () => {
    initDashboardAccordion()
    const toggle = document.getElementById('dashboard-nav__project--7')

    await collapse(toggle)

    expect(JSON.parse(Cookies.get(COOKIE_NAME))).toEqual([[7], []])
  })

  it('ignores malformed cookie values', async () => {
    Cookies.set(COOKIE_NAME, 'not-json')
    initDashboardAccordion()

    await collapse(document.getElementById('dashboard-nav__module--2'))

    expect(JSON.parse(Cookies.get(COOKIE_NAME))).toEqual([[], [2]])
  })

  it('normalizes a legacy flat cookie', async () => {
    Cookies.set(COOKIE_NAME, JSON.stringify([7]))
    initDashboardAccordion()

    await collapse(document.getElementById('dashboard-nav__module--2'))

    expect(JSON.parse(Cookies.get(COOKIE_NAME))).toEqual([[7], [2]])
  })

  it('drops invalid cookie entries', async () => {
    Cookies.set(COOKIE_NAME, JSON.stringify([[7], [2, 'x'], 9]))
    initDashboardAccordion()

    await collapse(document.getElementById('dashboard-nav__module--4'))

    expect(JSON.parse(Cookies.get(COOKIE_NAME))).toEqual([[7], [2, 4]])
  })

  it('toggles the accordion with Enter and Space', () => {
    initDashboardAccordion()
    const toggle = document.getElementById('dashboard-nav__module--2')
    const onClick = jest.fn()
    toggle.addEventListener('click', onClick)

    toggle.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }))
    toggle.dispatchEvent(new KeyboardEvent('keydown', { key: ' ', bubbles: true }))
    toggle.dispatchEvent(new KeyboardEvent('keydown', { key: 'a', bubbles: true }))

    expect(onClick).toHaveBeenCalledTimes(2)
  })
})
