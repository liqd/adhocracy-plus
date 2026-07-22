import React, { useEffect, useRef } from 'react'
import django from 'django'
import Uppy from '@uppy/core'
import Dashboard from '@uppy/dashboard'
import ImageEditor from '@uppy/image-editor'
import deDE from '@uppy/locales/lib/de_DE.js'
import enUS from '@uppy/locales/lib/en_US.js'

import FormFieldError from 'adhocracy4/adhocracy4/static/FormFieldError'

const UPPY_LOCALES = {
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

const UppyQuestionImageUpload = ({ id, question, onImageChange, errors, helpText, altText, onAltTextChange }) => {
  const uppyRef = useRef(null)
  const onImageChangeRef = useRef(onImageChange)

  onImageChangeRef.current = onImageChange

  const imageError = errors?.image_base64 || errors?.image
  const altTextError = errors?.image_alt_text

  useEffect(() => {
    let uppy

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
          rotate: false,
          granularRotate: false,
          cropSquare: false,
          cropWidescreen: false,
          cropWidescreenVertical: false
        },
        cropperOptions: {
          viewMode: 1,
          autoCropArea: 1
        }
      })

      uppy.on('file-added', (file) => {
        uppy.getPlugin('ImageEditor')?.stop()
        uppy.getFiles().forEach((existingFile) => {
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

      uppy.on('complete', (result) => {
        const file = result.successful[0] || uppy.getFiles()[0]
        if (file) {
          const reader = new FileReader()
          reader.onloadend = () => {
            onImageChangeRef.current(reader.result)
          }
          reader.readAsDataURL(file.data)
        }
        uppy.getPlugin('Dashboard')?.closeModal()
        uppy.getFiles().forEach((uppyFile) => {
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

      <FormFieldError id={`image-error-${id}`} error={errors} field="image_base64" />

      {(question.image_url || altTextError) && (
        <div className={`form-group ${altTextError ? 'has-error' : ''}`}>
          <label htmlFor={`id_questions-${id}-image_alt_text`}>
            {django.gettext('Alt text')}
          </label>
          <input
            type="text"
            id={`id_questions-${id}-image_alt_text`}
            className={`form-control ${altTextError ? 'is-invalid' : ''}`}
            value={altText || ''}
            onChange={(e) => onAltTextChange(e.target.value)}
            maxLength={80}
            aria-invalid={!!altTextError}
            aria-describedby={altTextError ? `alt-text-error-${id}` : undefined}
          />
          <FormFieldError id={`alt-text-error-${id}`} error={errors} field="image_alt_text" />
        </div>
      )}
    </div>
  )
}

export default UppyQuestionImageUpload
