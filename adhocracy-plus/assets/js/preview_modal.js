// Keep in sync with $breakpoint-down in _variables.scss (50rem).
const DESKTOP_PREVIEW_MIN_WIDTH_PX = 800

export function getDefaultPreviewDevice () {
  return window.matchMedia(`(min-width: ${DESKTOP_PREVIEW_MIN_WIDTH_PX}px)`).matches
    ? 'desktop'
    : 'mobile'
}

export function setPreviewDevice (previewModal, device) {
  if (!previewModal) return

  const frame = previewModal.querySelector('.preview-modal__frame')
  if (frame) {
    frame.classList.remove(
      'preview-modal__frame--desktop',
      'preview-modal__frame--mobile'
    )
    frame.classList.add(`preview-modal__frame--${device}`)
  }

  const toggle = previewModal.querySelector('.preview-modal__toggle')
  if (!toggle) return

  toggle.querySelectorAll('[data-preview-device]').forEach((button) => {
    const isActive = button.dataset.previewDevice === device
    button.classList.toggle('is-active', isActive)
    button.setAttribute('aria-pressed', isActive ? 'true' : 'false')
  })
}

export function bindPreviewDeviceToggle (root) {
  if (!root || root.dataset.previewDeviceBound) return
  root.dataset.previewDeviceBound = 'true'

  root.addEventListener('click', (event) => {
    const toggleButton = event.target.closest('[data-preview-device]')
    if (!toggleButton) return

    const previewModal = toggleButton.closest('.preview-modal')
    if (!previewModal) return

    event.preventDefault()
    setPreviewDevice(previewModal, toggleButton.dataset.previewDevice)
  })

  document.body.addEventListener('htmx:afterSwap', (event) => {
    if (!event.detail.target.classList.contains('modal-content')) return
    const previewModal = (
      event.detail.target.closest('.preview-modal') ||
      event.detail.target.querySelector('.preview-modal')
    )
    if (!previewModal) return
    setPreviewDevice(previewModal, getDefaultPreviewDevice())
  })
}
