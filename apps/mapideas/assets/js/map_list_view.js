/**
 * Map List View Toggle Functionality
 * Handles switching between map and list views on mobile devices
 */

document.addEventListener('DOMContentLoaded', function () {
  const mapView = document.getElementById('map-view')
  const listView = document.getElementById('list-view')
  const listBtn = document.querySelector('[data-view="list"]')
  const mapBtn = document.querySelector('[data-view="map"]')

  // Mobile Toggle
  document.querySelectorAll('[data-view]').forEach(btn => {
    btn.addEventListener('click', function () {
      const view = this.dataset.view

      const url = new URL(window.location)
      url.searchParams.set('mode', view)
      window.history.pushState({}, '', url)

      if (view === 'map') {
        toggleButtons(mapBtn, listBtn)
        toggleViews(listView, mapView)
      } else {
        toggleButtons(listBtn, mapBtn)
        toggleViews(mapView, listView)
      }
    })
  })
})

/**
 * Toggle button styles between default and light variants
 * @param {HTMLElement} becomeDefault - Button to become default style
 * @param {HTMLElement} becomeLight - Button to become light style
 */
function toggleButtons (becomeDefault, becomeLight) {
  becomeDefault.classList.replace('btn--light', 'btn--default')
  becomeLight.classList.replace('btn--default', 'btn--light')
}

/**
 * Toggle visibility between mobile views
 * @param {HTMLElement} mobileHide - Element to hide
 * @param {HTMLElement} mobileShow - Element to show
 */
function toggleViews (mobileHide, mobileShow) {
  mobileHide.classList.add('mobile-hide')
  mobileShow.classList.remove('mobile-hide')
  if (mobileShow.id === 'map-view') {
    // Dispatch a custom event when the map view is shown
    const event = new Event('mapViewShown')
    mobileShow.dispatchEvent(event)
  }
}
