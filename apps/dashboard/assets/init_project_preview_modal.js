import { bindPreviewDeviceToggle } from '../../../adhocracy-plus/assets/js/preview_modal'

function dispatchEmbedReady () {
  document.dispatchEvent(new Event('a4.embed.ready'))
}

function initPreviewIframe (previewModal) {
  const iframe = previewModal.querySelector('#project-preview-iframe')
  if (!iframe || iframe.dataset.previewInitialized) return

  iframe.dataset.previewInitialized = 'true'
  iframe.src = iframe.dataset.contentUrl
  iframe.addEventListener('load', dispatchEmbedReady)
}

function init () {
  const modalRoot = document.getElementById('modal-root')
  if (!modalRoot) return

  let lastPreviewTrigger = null

  bindPreviewDeviceToggle(modalRoot)

  document.body.addEventListener('click', (event) => {
    const trigger = event.target.closest('.js-project-preview-trigger')
    if (!trigger) return

    lastPreviewTrigger = trigger
    trigger.blur()
  })

  document.body.addEventListener('htmx:afterSwap', (event) => {
    if (!event.detail.target.classList.contains('modal-content')) return
    const previewModal = event.detail.target.querySelector('.preview-modal')
    if (!previewModal) return

    initPreviewIframe(previewModal)
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
