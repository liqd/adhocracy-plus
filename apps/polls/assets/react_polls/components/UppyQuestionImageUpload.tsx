import React, { useEffect, useRef } from 'react'
import django from 'django'
import Uppy from '@uppy/core'
import Dashboard from '@uppy/dashboard'
import ImageEditor from '@uppy/image-editor'
import deDE from '@uppy/locales/lib/de_DE.js'
import enUS from '@uppy/locales/lib/en_US.js'

import FieldError from './FieldError'

const UPPY_LOCALES: Record<string, typeof deDE> = {
  de: deDE,
  en: enUS
}

function getUppyLocale () {
  const pageLanguage = (document.documentElement.lang || 'en').toLowerCase()
  if (UPPY_LOCALES[pageLanguage]) {
    return UPPY_LOCALES[pageLanguage]
  }

  const languageCode = pageLanguage.split('-')[0]
  return UPPY_LOCALES[languageCode] || enUS
}

const MIN_WIDTH = 1500
const MIN_HEIGHT = 500
const MAX_LONGEST_SIDE = 2000
const JPEG_QUALITY = 0.85

/**
 * Resizes and re-encodes an uploaded image so the request body stays small
 * (the image is sent as base64 in the JSON body, which is ~33% larger).
 * Opaque images become JPEG, images with transparency stay PNG. The configured
 * minimum resolution is never undercut and the smaller of the two results is
 * kept.
 */
const compressImageDataUrl = (dataUrl: string): Promise<string> => new Promise((resolve) => {
  const image = new Image()
  image.onload = () => {
    const sourceWidth = image.naturalWidth || image.width
    const sourceHeight = image.naturalHeight || image.height
    if (!sourceWidth || !sourceHeight) {
      resolve(dataUrl)
      return
    }

    const longestSide = Math.max(sourceWidth, sourceHeight)
    let scale = longestSide > MAX_LONGEST_SIDE ? MAX_LONGEST_SIDE / longestSide : 1
    // never shrink below the required minimum resolution
    scale = Math.min(1, Math.max(scale, MIN_WIDTH / sourceWidth, MIN_HEIGHT / sourceHeight))
    const width = Math.max(1, Math.round(sourceWidth * scale))
    const height = Math.max(1, Math.round(sourceHeight * scale))

    const canvas = document.createElement('canvas')
    canvas.width = width
    canvas.height = height
    const context = canvas.getContext('2d')
    if (!context) {
      resolve(dataUrl)
      return
    }
    context.drawImage(image, 0, 0, width, height)

    let hasTransparency = false
    try {
      const pixels = context.getImageData(0, 0, width, height).data
      for (let i = 3; i < pixels.length; i += 4) {
        if (pixels[i] < 255) {
          hasTransparency = true
          break
        }
      }
    } catch {
      hasTransparency = true
    }

    const compressed = hasTransparency
      ? canvas.toDataURL('image/png')
      : canvas.toDataURL('image/jpeg', JPEG_QUALITY)
    resolve(compressed.length < dataUrl.length ? compressed : dataUrl)
  }
  image.onerror = () => resolve(dataUrl)
  image.src = dataUrl
})

interface UppyQuestionImageUploadProps {
  id: string | number
  question: { image_url?: string | null }
  onImageChange: (base64: string) => void
  errors?: Record<string, unknown>
  helpText?: string
  altText?: string
  onAltTextChange: (value: string) => void
}

const UppyQuestionImageUpload = ({ id, question, onImageChange, errors, helpText, altText, onAltTextChange }: UppyQuestionImageUploadProps) => {
  const uppyRef = useRef<any>(null)
  const onImageChangeRef = useRef(onImageChange)

  onImageChangeRef.current = onImageChange

  const imageError = Boolean(errors?.image_base64 || errors?.image)
  const altTextError = Boolean(errors?.image_alt_text)

  useEffect(() => {
    let uppy: any

    try {
      uppy = new Uppy({
        autoProceed: false,
        locale: getUppyLocale(),
        restrictions: {
          maxNumberOfFiles: 1,
          allowedFileTypes: ['image/*']
        }
      })

      uppy.use(Dashboard, {
        target: document.body,
        inline: false,
        hideUploadButton: true,
        proudlyDisplayPoweredByUppy: false,
        autoOpen: 'imageEditor',
        note: django.gettext('Images are resized and compressed automatically before you save the form.')
      })

      uppy.use(ImageEditor, {
        quality: 0.8,
        actions: {
          revert: true,
          rotate: true,
          zoomIn: true,
          zoomOut: true,
          flip: false,
          granularRotate: false,
          cropSquare: false,
          cropWidescreen: false,
          cropWidescreenVertical: false,
        },
        cropperOptions: {
          viewMode: 1,
          autoCropArea: 1
        }
      })

      uppy.on('file-added', (file: any) => {
        uppy.getPlugin('ImageEditor')?.stop()
        uppy.getFiles().forEach((existingFile: any) => {
          if (existingFile.id !== file.id) {
            uppy.removeFile(existingFile.id)
          }
        })
      })

      uppy.on('file-editor:cancel', () => {
        uppy.getPlugin('ImageEditor')?.stop()
      })

      uppy.on('file-editor:complete', () => {
        uppy.upload().catch(() => {})
      })

      uppy.on('complete', (result: any) => {
        const file = result.successful[0] || uppy.getFiles()[0]
        if (file) {
          const reader = new FileReader()
          reader.onloadend = () => {
            compressImageDataUrl(reader.result as string)
              .then((compressed) => {
                onImageChangeRef.current(compressed)
                return undefined
              })
              .catch(() => undefined)
          }
          reader.readAsDataURL(file.data)
        }
        uppy.getPlugin('Dashboard')?.closeModal()
        uppy.getFiles().forEach((uppyFile: any) => {
          uppy.removeFile(uppyFile.id)
        })
      })

      uppy.on('file-removed', () => {
        if (uppy.getFiles().length === 0) {
          onImageChangeRef.current('')
        }
      })

      uppyRef.current = uppy
    } catch (e) {
      console.error('UppyQuestionImageUpload: Uppy init failed', e)
    }

    return () => {
      if (uppy) {
        uppy.destroy()
      }
    }
  }, [])

  const handleRemove = () => {
    onImageChange('')
  }

  return (
    <div className="question-image-upload form-group">
      <label id={`image-upload-label-${id}`}>
        {django.gettext('Question image')}
      </label>

      {helpText && <div className="form-hint">{helpText}</div>}

      <div className={`image-upload-container ${imageError ? 'is-invalid' : ''}`}>
        <span className="image-upload-text">
          {question.image_url
            ? django.gettext('Image uploaded')
            : django.gettext('No image uploaded')}
        </span>

        <div className="image-upload-actions">
          {question.image_url && (
            <img
              id={`image-preview-${id}`}
              src={question.image_url}
              alt={django.gettext('Preview')}
              className="image-upload-preview"
            />
          )}

          <button
            type="button"
            onClick={() => {
              uppyRef.current?.getPlugin('Dashboard')?.openModal()
            }}
            className="image-upload-upload-btn"
            aria-label={django.gettext('Upload image')}
            title={django.gettext('Upload image')}
          >
            <i className="fa fa-cloud-upload" aria-hidden="true" />
          </button>

          {question.image_url && (
            <button
              type="button"
              className="image-upload-remove-btn"
              onClick={handleRemove}
              aria-label={django.gettext('Remove image')}
              title={django.gettext('Remove image')}
            >
              <i className="fa fa-times" aria-hidden="true" />
            </button>
          )}
        </div>
      </div>

      <FieldError id={`image-error-${id}`} error={errors} field="image_base64" />

      {question.image_url && (
        <div className={`form-group ${altTextError ? 'has-error' : ''}`}>
          <label htmlFor={`id_questions-${id}-image_alt_text`}>
            {django.gettext('Alt text')}
            <span
              role="presentation"
              title={django.gettext('This field is required')}
            >
              *
            </span>
          </label>
          <input
            type="text"
            id={`id_questions-${id}-image_alt_text`}
            className={`form-control ${altTextError ? 'is-invalid' : ''}`}
            value={altText || ''}
            onChange={(e) => onAltTextChange(e.target.value)}
            maxLength={80}
            required
            aria-invalid={!!altTextError}
            aria-describedby={altTextError ? `alt-text-error-${id}` : undefined}
          />
          <FieldError id={`alt-text-error-${id}`} error={errors} field="image_alt_text" />
        </div>
      )}
    </div>
  )
}

export default UppyQuestionImageUpload
