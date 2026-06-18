import Uppy from '@uppy/core'
import Dashboard from '@uppy/dashboard'
import ImageEditor from '@uppy/image-editor'
import Compressor from '@uppy/compressor'

import '@uppy/core/css/style.min.css'
import '@uppy/dashboard/css/style.min.css'
import '@uppy/image-editor/css/style.min.css'
import './uppy_image_upload.scss'

const PLACEHOLDER_SRC = 'data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs='

function getStorageKey (inputId) {
  return 'image_upload_' + window.location.pathname + '_' + inputId
}

function saveToSessionStorage (inputId, file) {
  const reader = new FileReader()
  reader.addEventListener('load', (e) => {
    try {
      sessionStorage.setItem(
        getStorageKey(inputId),
        JSON.stringify({
          dataUrl: e.target.result,
          fileName: file.name,
          fileSize: file.size,
          timestamp: Date.now(),
          pagePath: window.location.pathname
        })
      )
    } catch (err) {
      console.warn('Could not save image to sessionStorage:', err)
    }
  })
  reader.readAsDataURL(file)
}

function clearSessionStorage (inputId) {
  sessionStorage.removeItem(getStorageKey(inputId))
}

function readConfig (container) {
  const aspectRatio = parseFloat(container.dataset.aspectRatio, 10)
  return {
    inputId: container.dataset.inputId,
    minWidth: parseInt(container.dataset.minWidth, 10) || 0,
    minHeight: parseInt(container.dataset.minHeight, 10) || 0,
    outputWidth: parseInt(container.dataset.outputWidth, 10) || 0,
    outputHeight: parseInt(container.dataset.outputHeight, 10) || 0,
    aspectRatio: Number.isFinite(aspectRatio) ? aspectRatio : null,
    maxWidth: parseInt(container.dataset.maxWidth, 10) || 0
  }
}

function initContainer (container) {
  if (container.dataset.uppyInitialized) {
    return
  }

  const config = readConfig(container)
  const input = document.getElementById(config.inputId)
  const uploadField = container.closest('.uppy-image-upload-field')
  const trigger = uploadField?.querySelector('[data-uppy-trigger]')
  const actionParent = uploadField?.querySelector('.upload-wrapper__action-parent')
  if (!input || !trigger || !actionParent) {
    return
  }

  actionParent.insertBefore(trigger, actionParent.firstChild)

  container.dataset.uppyInitialized = 'true'

  const clearCheckbox = document.querySelector(
    'input[data-upload-clear="' + config.inputId + '"]'
  )

  const clearUploadedFile = (keepDeleteChecked = false) => {
    clearSessionStorage(config.inputId)
    input.value = ''

    const previewImage = document.querySelector(
      'img[data-upload-preview="' + config.inputId + '"]'
    )
    if (previewImage) {
      previewImage.setAttribute('src', PLACEHOLDER_SRC)
    }

    const text = document.querySelector('#text-' + config.inputId)
    if (text) {
      text.value = ''
      text.style.color = ''
    }

    if (clearCheckbox && !keepDeleteChecked) {
      clearCheckbox.checked = false
    }
  }

  const syncFileToInput = (file) => {
    if (!file?.data) {
      return
    }

    const blob = file.data
    const imageFile = new File(
      [blob],
      file.name,
      { type: file.type || blob.type, lastModified: Date.now() }
    )

    const dataTransfer = new DataTransfer()
    dataTransfer.items.add(imageFile)
    input.files = dataTransfer.files

    saveToSessionStorage(config.inputId, imageFile)

    if (clearCheckbox) {
      clearCheckbox.checked = false
    }

    input.dispatchEvent(new Event('change', { bubbles: true }))
  }

  let suppressFileRemovedHandler = false

  const uppy = new Uppy({
    autoProceed: false,
    restrictions: {
      maxNumberOfFiles: 1,
      allowedFileTypes: ['image/*']
    }
  })

  uppy.use(Dashboard, {
    target: document.body,
    inline: false,
    trigger,
    hideUploadButton: true,
    proudlyDisplayPoweredByUppy: false,
    autoOpen: 'imageEditor',
    note: 'Images are resized and compressed automatically before you save the form.'
  })

  uppy.use(ImageEditor, {
    quality: 0.8,
    actions: {
      rotate: false,
      granularRotate: false,
      cropSquare: false,
      cropWidescreen: false,
      cropWidescreenVertical: false
    },
    cropperOptions: {
      viewMode: 1,
      autoCropArea: 1,
      ...(config.aspectRatio ? { aspectRatio: config.aspectRatio } : {}),
      croppedCanvasOptions: config.outputWidth && config.outputHeight
        ? {
            width: config.outputWidth,
            height: config.outputHeight,
            imageSmoothingQuality: 'high'
          }
        : {
            minWidth: config.minWidth,
            minHeight: config.minHeight
          }
    }
  })

  const compressorOptions = { quality: 0.8 }
  if (config.outputWidth && config.outputHeight) {
    compressorOptions.width = config.outputWidth
    compressorOptions.height = config.outputHeight
  } else if (config.maxWidth) {
    compressorOptions.maxWidth = config.maxWidth
  }

  uppy.use(Compressor, compressorOptions)

  uppy.on('file-added', (file) => {
    uppy.getFiles().forEach((existingFile) => {
      if (existingFile.id !== file.id) {
        uppy.removeFile(existingFile.id)
      }
    })
  })

  uppy.on('file-editor:complete', () => {
    uppy.upload().catch(() => {})
  })

  uppy.on('complete', (result) => {
    const file = result.successful[0] || uppy.getFiles()[0]
    if (file) {
      syncFileToInput(file)
      uppy.getPlugin('ImageEditor')?.stop()
      suppressFileRemovedHandler = true
      uppy.getFiles().forEach((uppyFile) => {
        uppy.removeFile(uppyFile.id)
      })
      suppressFileRemovedHandler = false
    }
    uppy.getPlugin('Dashboard')?.closeModal()
  })

  uppy.on('dashboard:modal-open', () => {
    if (uppy.getFiles().length > 0 || clearCheckbox?.checked) {
      return
    }

    const existingFile = input.files?.[0]
    if (!existingFile) {
      return
    }

    uppy.addFile({
      name: existingFile.name,
      type: existingFile.type,
      data: existingFile,
      source: 'local'
    })
  })

  uppy.on('file-removed', () => {
    if (suppressFileRemovedHandler) {
      return
    }
    if (uppy.getFiles().length === 0 && !clearCheckbox?.checked) {
      clearUploadedFile()
    }
  })

  if (clearCheckbox) {
    clearCheckbox.addEventListener('change', (e) => {
      if (e.target.checked) {
        suppressFileRemovedHandler = true
        uppy.getFiles().forEach((file) => {
          uppy.removeFile(file.id)
        })
        clearUploadedFile(true)
        suppressFileRemovedHandler = false
      }
    })
  }
}

function init () {
  document.querySelectorAll('[data-uppy-image-upload]').forEach(initContainer)
}

function boot () {
  init()
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', boot, false)
} else {
  boot()
}
document.addEventListener('a4.embed.ready', boot, false)
