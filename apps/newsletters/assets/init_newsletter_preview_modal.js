/* global django */
import { bindPreviewDeviceToggle } from '../../../adhocracy-plus/assets/js/preview_modal'

const MODAL_ID = 'newsletter-preview-modal'
const PREVIEW_TRIGGER = '.js-newsletter-preview-trigger'
const TEST_TRIGGER = '.js-newsletter-test-send'
const STATUS_SELECTOR = '.js-newsletter-test-status'
const STATUS_DISMISS_MS = 8000
const STATUS_FADE_MS = 300

function clearTestStatus () {
  document.querySelectorAll(STATUS_SELECTOR).forEach((status) => {
    window.clearTimeout(status._newsletterStatusTimer)
    if (!status.innerHTML.trim()) return

    status.classList.add('is-fading')
    window.setTimeout(() => {
      status.innerHTML = ''
      status.classList.remove('is-fading')
    }, STATUS_FADE_MS)
  })
}

function scheduleStatusDismiss (status) {
  const alert = status.querySelector('[data-autodismiss]')
  if (!alert) return

  window.clearTimeout(status._newsletterStatusTimer)
  status.classList.remove('is-fading')
  status._newsletterStatusTimer = window.setTimeout(() => {
    status.classList.add('is-fading')
    window.setTimeout(() => {
      status.innerHTML = ''
      status.classList.remove('is-fading')
    }, STATUS_FADE_MS)
  }, STATUS_DISMISS_MS)
}

function bindEditorChangeHandlers () {
  if (!window.editors) return

  Object.values(window.editors).forEach((editor) => {
    if (!editor || editor.__newsletterStatusBound) return
    editor.__newsletterStatusBound = true

    if (editor.model && editor.model.document) {
      editor.model.document.on('change:data', clearTestStatus)
    }
  })
}

function syncEditors () {
  bindEditorChangeHandlers()
  if (!window.editors) return

  Object.values(window.editors).forEach((editor) => {
    if (editor && typeof editor.updateSourceElement === 'function') {
      editor.updateSourceElement()
    }
  })
}

function init () {
  const modal = document.getElementById(MODAL_ID)
  if (!modal) return

  const modalContent = modal.querySelector('.modal-content')
  const loadingHtml = modalContent ? modalContent.innerHTML : ''
  const form = document.getElementById('newsletter-form')
  let lastTrigger = null

  bindPreviewDeviceToggle(modal)

  if (form) {
    form.addEventListener('input', clearTestStatus)
    form.addEventListener('change', clearTestStatus)
  }

  document.addEventListener('click', (event) => {
    const trigger = event.target.closest(PREVIEW_TRIGGER)
    if (trigger) {
      lastTrigger = trigger
      syncEditors()
      return
    }

    if (event.target.closest(TEST_TRIGGER)) {
      syncEditors()
    }
  }, true)

  document.body.addEventListener('htmx:afterSwap', (event) => {
    if (!event.detail.target.matches(STATUS_SELECTOR)) return

    scheduleStatusDismiss(event.detail.target)

    const previewBody = event.detail.target.closest('.preview-modal__body')
    if (previewBody) {
      window.requestAnimationFrame(() => {
        previewBody.scrollTo({
          top: previewBody.scrollHeight,
          behavior: 'smooth'
        })
      })
    }
  })

  document.body.addEventListener('htmx:responseError', (event) => {
    if (!modalContent || event.detail.target !== modalContent) return

    modalContent.innerHTML = (
      '<div class="modal-body">' +
        '<div class="alert alert--danger" role="alert">' +
          django.gettext('The preview could not be loaded. Please try again.') +
        '</div>' +
      '</div>'
    )
  })

  modal.addEventListener('hidden.bs.modal', () => {
    if (modalContent) modalContent.innerHTML = loadingHtml

    if (lastTrigger && document.contains(lastTrigger)) {
      lastTrigger.focus()
    }
    lastTrigger = null
  })
}

document.addEventListener('DOMContentLoaded', init, false)
