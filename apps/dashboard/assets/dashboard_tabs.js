'use strict'

/*
 * This improves accessibility of tabs on dashboard pages where applying Bootstrap's
 * built-in tab functionality is not possible. It ensures consistent keyboard navigability
 * in both scenarios.
 *
 * This solution is based on the official W3C WAI example for tabs with manual activation:
 * https://www.w3.org/WAI/ARIA/apg/patterns/tabs/examples/tabs-manual/
 */

class DashboardTabs {
  constructor (tablist) {
    this.tablist = tablist
    this.firstTab = null
    this.lastTab = null
    this.tabs = Array.from(this.tablist.querySelectorAll('[role=tab]'))
    this.tabs.forEach(tab => {
      tab.addEventListener('keydown', this.onKeyDown.bind(this))
      if (!this.firstTab) {
        this.firstTab = tab
      }
      this.lastTab = tab
    })
  }

  focusTab (tab) {
    tab.focus()
  }

  focusPreviousTab (currentTab) {
    if (currentTab === this.firstTab) {
      this.focusTab(this.lastTab)
    } else {
      this.focusTab(this.tabs[this.tabs.indexOf(currentTab) - 1])
    }
  }

  focusNextTab (currentTab) {
    if (currentTab === this.lastTab) {
      this.focusTab(this.firstTab)
    } else {
      this.focusTab(this.tabs[this.tabs.indexOf(currentTab) + 1])
    }
  }

  onKeyDown (event) {
    const currentTab = event.currentTarget

    switch (event.key) {
      case 'ArrowLeft':
        this.focusPreviousTab(currentTab)
        break
      case 'ArrowUp':
        this.focusPreviousTab(currentTab)
        event.preventDefault()
        break
      case 'ArrowRight':
        this.focusNextTab(currentTab)
        break
      case 'ArrowDown':
        this.focusNextTab(currentTab)
        event.preventDefault()
        break
      case 'Home':
        this.focusTab(this.firstTab)
        break
      case 'End':
        this.focusTab(this.lastTab)
        break
      default:
        break
    }
  }
}

window.addEventListener('load', () => {
  const tablists = document.querySelectorAll('[role=tablist].dashboard-tabs')
  tablists.forEach(tablist => {
    tablist = new DashboardTabs(tablist)
  })
})
