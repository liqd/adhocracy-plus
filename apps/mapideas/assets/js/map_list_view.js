/**
 * Map List View Toggle Functionality
 * Handles switching between map and list views on mobile devices
 */

import django from 'django'

document.addEventListener('DOMContentLoaded', function () {
  const mapView = document.getElementById('map-view')
  const listView = document.getElementById('list-view')
  const listBtn = document.querySelector('[data-view="list"]')
  const mapBtn = document.querySelector('[data-view="map"]')
  const desktop = window.matchMedia('(min-width: 768px)')
  let mapInstance = null
  let clusterGroup = null

  // Prevent interactive elements inside a list card header (links, buttons,
  // details content) or text selection from toggling the card's collapse.
  window.addEventListener('click', function (event) {
    if (!event.target.closest('.map-list-view .list-item__header')) {
      return
    }
    const hasSelection = window.getSelection && window.getSelection().toString().trim() !== ''
    if (hasSelection || event.target.closest('a, button, .list-item__details')) {
      event.stopPropagation()
    }
  }, true)

  // On desktop the list is selection-based (like the ideas inbox), so the
  // headers must not trigger Bootstrap's inline collapse.
  if (desktop.matches) {
    document.querySelectorAll('.map-list-view .list-item__header').forEach(function (header) {
      header.removeAttribute('data-bs-toggle')
      header.removeAttribute('data-bs-target')
      header.removeAttribute('data-bs-parent')
    })
  }

  // Decorate the map popup so it mirrors a list card: category badge, title,
  // comment indicator (already provided by the map bundle) and a "Show details"
  // link with a right caret that navigates to the item detail page.
  const categoriesScript = document.querySelector('script[data-mapidea-categories]')
  const categoriesByUrl = {}
  if (categoriesScript) {
    try {
      JSON.parse(categoriesScript.textContent).forEach(function (entry) {
        if (entry && entry.url) {
          categoriesByUrl[entry.url] = entry.category
        }
      })
    } catch {
      // Ignore malformed data and render the popup without categories.
    }
  }

  function decoratePopup (popupInstance) {
    if (!popupInstance) {
      return
    }
    const popup = popupInstance.getElement()
    if (!popup || popup.dataset.mapideaDecorated === 'true') {
      return
    }
    const name = popup.querySelector('.maps-popups-popup-name')
    const link = name && name.querySelector('a')
    if (!name || !link) {
      return
    }
    popup.dataset.mapideaDecorated = 'true'
    popup.classList.add('maps-popups--list-item')

    const url = link.getAttribute('href')
    const textContent = popup.querySelector('.maps-popups-popup-text-content') || popup
    const meta = popup.querySelector('.maps-popups-popup-meta')
    const comments = popup.querySelector('.map-popup-comments-count')
    const category = categoriesByUrl[url]

    // Title above the ratings/comments meta.
    if (meta) {
      textContent.insertBefore(name, meta)
    }

    if (category) {
      const labels = document.createElement('div')
      labels.className = 'list-item__labels maps-popups-popup-labels'
      const badge = document.createElement('span')
      badge.className = 'badge badge--big list-item__badge--category'
      badge.textContent = category
      labels.appendChild(badge)
      textContent.insertBefore(labels, textContent.firstChild)
    }

    // Comment indicator: icon before count, matching the list cards.
    if (comments) {
      const icon = comments.querySelector('i')
      if (icon) {
        comments.insertBefore(icon, comments.firstChild)
      }
      comments.classList.add('list-item__comments')
    }

    const footer = document.createElement('div')
    footer.className = 'maps-popups-popup-footer'
    if (comments) {
      footer.appendChild(comments)
    }
    const details = document.createElement('a')
    details.className = 'list-item__expand-toggle'
    details.href = url
    details.appendChild(document.createTextNode(django.gettext('Show details') + ' '))
    const caret = document.createElement('i')
    caret.className = 'fas fa-chevron-right'
    caret.setAttribute('aria-hidden', 'true')
    details.appendChild(caret)
    footer.appendChild(details)
    textContent.appendChild(footer)

    // Drop the ratings meta row if it is now empty (e.g. no ratings).
    if (meta && meta.children.length === 0) {
      meta.remove()
    }

    // Leaflet sized the popup before this decoration ran, so re-render to make
    // it measure the injected content (otherwise it stays narrow and wraps).
    const contentEl = popup.querySelector('.leaflet-popup-content')
    if (contentEl) {
      popupInstance.options.maxWidth = 320
      popupInstance.setContent(contentEl.innerHTML)
    }
  }

  // Selection state shared by the desktop list and the map pins.
  function findCardByUrl (href) {
    const cards = document.querySelectorAll('.map-list-view .list-item--card')
    for (const card of cards) {
      const cardLink = card.querySelector('.list-item__title-link')
      if (cardLink && cardLink.href === href) {
        return card
      }
    }
    return null
  }

  function applySelection (card) {
    const pk = card ? card.getAttribute('data-mapidea-pk') : null
    document.querySelectorAll('.map-list-view .list-item--card').forEach(function (item) {
      const isSelected = item === card
      item.classList.toggle('selected', isSelected)
      const header = item.querySelector('.list-item__header')
      if (header) {
        header.setAttribute('aria-expanded', isSelected ? 'true' : 'false')
      }
    })
    document.querySelectorAll('.map-list-view [data-mapidea-pane]').forEach(function (pane) {
      pane.hidden = pane.getAttribute('data-mapidea-pane') !== pk
    })
    const placeholder = document.querySelector('.map-list-view [data-mapidea-pane-placeholder]')
    if (placeholder) {
      placeholder.hidden = !!pk
    }
  }

  function findMarkerByUrl (href) {
    if (!clusterGroup) {
      return null
    }
    let found = null
    clusterGroup.eachLayer(function (marker) {
      if (found || !marker.getPopup) {
        return
      }
      const popup = marker.getPopup()
      const content = popup && popup.getContent()
      if (typeof content !== 'string') {
        return
      }
      const tmp = document.createElement('div')
      tmp.innerHTML = content
      const link = tmp.querySelector('.maps-popups-popup-name a')
      if (link && link.href === href) {
        found = marker
      }
    })
    return found
  }

  // Selecting a card centers/opens its pin; deselecting closes the popup.
  function focusCard (card) {
    applySelection(card)
    if (card) {
      const link = card.querySelector('.list-item__title-link')
      const marker = link && findMarkerByUrl(link.href)
      if (marker && clusterGroup && mapInstance) {
        clusterGroup.zoomToShowLayer(marker, function () {
          marker.openPopup()
        })
      }
    } else if (mapInstance) {
      mapInstance.closePopup()
    }
  }

  const listRoot = document.querySelector('.map-list-view')
  if (listRoot) {
    listRoot.addEventListener('click', function (event) {
      if (!desktop.matches || event.target.closest('a, button, .list-item__details')) {
        return
      }
      const header = event.target.closest('.list-item__header')
      if (!header) {
        return
      }
      const card = header.closest('.list-item')
      focusCard(card.classList.contains('selected') ? null : card)
    })
  }

  document.querySelectorAll('.map-list-view [data-mapidea-hide-details]').forEach(function (btn) {
    btn.addEventListener('click', function (event) {
      event.preventDefault()
      focusCard(null)
    })
  })

  if (categoriesScript && window.L && window.L.Map) {
    window.L.Map.addInitHook(function () {
      mapInstance = this
      this.on('layeradd', function (event) {
        if (event.layer && typeof event.layer.zoomToShowLayer === 'function') {
          clusterGroup = event.layer
        }
      })
      this.on('popupopen', function (event) {
        decoratePopup(event.popup)
        if (desktop.matches) {
          const popup = event.popup && event.popup.getElement()
          const link = popup && popup.querySelector('.maps-popups-popup-name a')
          if (link) {
            applySelection(findCardByUrl(link.href))
          }
        }
      })
    })
  }

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
