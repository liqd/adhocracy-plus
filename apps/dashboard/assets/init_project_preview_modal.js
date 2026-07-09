function dispatchEmbedReady () {
  document.dispatchEvent(new Event('a4.embed.ready'))
}

// Keep in sync with $breakpoint-down in _variables.scss (50rem).
const DESKTOP_PREVIEW_MIN_WIDTH_PX = 800

function getDefaultPreviewDevice () {
  return window.matchMedia(`(min-width: ${DESKTOP_PREVIEW_MIN_WIDTH_PX}px)`).matches
    ? 'desktop'
    : 'mobile'
}

function initPreviewIframe (previewModal) {
  const iframe = previewModal.querySelector('#project-preview-iframe')
  if (!iframe || iframe.dataset.previewInitialized) return

  iframe.dataset.previewInitialized = 'true'
  iframe.src = iframe.dataset.contentUrl
  iframe.addEventListener('load', dispatchEmbedReady)
}

function setPreviewDevice (previewModal, device) {
  if (!previewModal) return

  const frame = previewModal.querySelector('#project-preview-frame')
  if (frame) {
    frame.classList.remove(
      'project-preview-modal__frame--desktop',
      'project-preview-modal__frame--mobile'
    )
    frame.classList.add(`project-preview-modal__frame--${device}`)
  }

  const toggle = previewModal.querySelector('.project-preview-modal__toggle')
  if (!toggle) return

  toggle.querySelectorAll('[data-preview-device]').forEach((button) => {
    const isActive = button.dataset.previewDevice === device
    button.classList.toggle('is-active', isActive)
    button.setAttribute('aria-pressed', isActive ? 'true' : 'false')
  })
}

function init () {
  const modalRoot = document.getElementById('modal-root')
  if (!modalRoot) return

  let lastPreviewTrigger = null

  document.body.addEventListener('click', (event) => {
    const trigger = event.target.closest('.js-project-preview-trigger')
    if (trigger) {
      lastPreviewTrigger = trigger
      trigger.blur()
    }

    const toggleButton = event.target.closest('[data-preview-device]')
    if (!toggleButton) return

    const previewModal = toggleButton.closest('.project-preview-modal')
    if (!previewModal) return

    event.preventDefault()
    setPreviewDevice(previewModal, toggleButton.dataset.previewDevice)
  })

  document.body.addEventListener('htmx:afterSwap', (event) => {
    if (!event.detail.target.classList.contains('modal-content')) return
    const previewModal = event.detail.target.querySelector('.project-preview-modal')
    if (!previewModal) return

    initPreviewIframe(previewModal)
    setPreviewDevice(previewModal, getDefaultPreviewDevice())
  })

  modalRoot.addEventListener('hidden.bs.modal', () => {
    modalRoot.querySelector('.modal-content').innerHTML = ''
    if (lastPreviewTrigger) {
      lastPreviewTrigger.blur()
      lastPreviewTrigger = null
    }
  })
}

document.addEventListener('DOMContentLoaded', init, false)
