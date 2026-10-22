/* global django */
import { bindPreviewDeviceToggle } from '../../../adhocracy-plus/assets/js/preview_modal'

const MODAL_ID = 'newsletter-preview-modal'
const PREVIEW_TRIGGER = '.js-newsletter-preview-trigger'
const TEST_TRIGGER = '.js-newsletter-test-send'

function syncEditors () {
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
  let lastTrigger = null

  bindPreviewDeviceToggle(modal)

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
