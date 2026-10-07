import { Dropdown, Modal } from 'bootstrap'

// Fallback list; the canonical one is rendered into #auth-modal as
// data-auth-views so it stays in sync with the Django URL configuration.
const DEFAULT_AUTH_VIEW_PATHS = [
  '/accounts/login/',
  '/accounts/signup/',
  '/accounts/guests/login/'
]

const MODAL_ID = 'auth-modal'
const MODAL_BODY_ID = 'auth-modal-body'

let authViewPaths = null

function getAuthViewPaths () {
  const modalElement = document.getElementById(MODAL_ID)
  const raw = modalElement && modalElement.dataset.authViews
  if (raw) {
    try {
      const paths = JSON.parse(raw)
      if (Array.isArray(paths) && paths.length > 0) {
        return new Set(
          paths.map((path) => new URL(path, window.location.origin).pathname)
        )
      }
    } catch {
      // Fall back to the defaults below.
    }
  }
  return new Set(DEFAULT_AUTH_VIEW_PATHS)
}

function getAuthPath (anchor) {
  if (!anchor || !anchor.href) return null
  if (!authViewPaths) authViewPaths = getAuthViewPaths()
  let path
  try {
    path = new URL(anchor.href, window.location.origin).pathname
  } catch {
    return null
  }
  return authViewPaths.has(path) ? path : null
}

function shouldIgnore (anchor) {
  if (!anchor || anchor.target || anchor.hasAttribute('download')) return true
  // Links that already opt into a custom htmx behaviour keep it.
  if (anchor.hasAttribute('hx-get') || anchor.hasAttribute('hx-post')) return true
  return false
}

function openInModal (anchor) {
  const modalElement = document.getElementById(MODAL_ID)
  const modalBody = document.getElementById(MODAL_BODY_ID)
  const url = anchor.getAttribute('href')
  if (!modalElement || !modalBody || !url || !window.htmx) return false

  // The trigger often lives in a menu (e.g. the mobile user indicator);
  // close it so it does not stay open behind the modal.
  document
    .querySelectorAll('[data-bs-toggle="dropdown"][aria-expanded="true"]')
    .forEach((toggle) => Dropdown.getOrCreateInstance(toggle).hide())

  window.htmx.ajax('GET', url, {
    target: `#${MODAL_BODY_ID}`,
    swap: 'innerHTML'
  })
  Modal.getOrCreateInstance(modalElement).show()
  document.body.classList.add('auth-modal-open')
  return true
}

function init () {
  const modalElement = document.getElementById(MODAL_ID)
  if (!modalElement) return

  // Reset the swapped content so a reopened modal never shows stale state.
  modalElement.addEventListener('hidden.bs.modal', function () {
    document.body.classList.remove('auth-modal-open')
    const modalBody = document.getElementById(MODAL_BODY_ID)
    if (modalBody) modalBody.innerHTML = ''
  })

  // Delegate clicks so auth links on any page (and inside the modal itself)
  // open in the modal via htmx. Without JavaScript the plain href still loads
  // the full page.
  document.addEventListener('click', function (event) {
    if (event.defaultPrevented || event.button !== 0) return
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return

    const anchor = event.target.closest('a[href]')
    if (shouldIgnore(anchor)) return
    if (!getAuthPath(anchor)) return

    if (openInModal(anchor)) {
      event.preventDefault()
    }
  })
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init)
} else {
  init()
}
