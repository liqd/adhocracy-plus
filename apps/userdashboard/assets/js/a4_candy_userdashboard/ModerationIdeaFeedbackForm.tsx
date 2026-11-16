import React, { useEffect, useRef, useState } from 'react'
import django from 'django'
import type { ModeratorFeedback, ModerationItem } from './types'

const FEEDBACK_MAX_LENGTH = 1000

declare global {
  interface Window {
    ClassicEditor?: any
  }
}

interface ModerationIdeaFeedbackFormProps {
  item: ModerationItem
  initialFeedback?: ModeratorFeedback | null
  ckeditorConfig?: string
  onSubmit: (payload: { feedback: string, status: string | null }) => void | Promise<void>
  onCancel: () => void
}

function plainTextLength (html: string) {
  if (typeof DOMParser === 'undefined') {
    return html.replace(/<[^>]*>/g, '').length
  }
  const doc = new DOMParser().parseFromString(html, 'text/html')
  return doc.body.textContent?.length ?? 0
}

export const ModerationIdeaFeedbackForm = (props: ModerationIdeaFeedbackFormProps) => {
  const { item, initialFeedback } = props
  const editorContainerRef = useRef<HTMLDivElement>(null)
  const [feedback, setFeedback] = useState(initialFeedback?.feedback_text || '')
  const [status, setStatus] = useState(item.moderator_status || '')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const formId = 'moderation-feedback-' + item.pk
  const supportsRichText = typeof window !== 'undefined' && !!window.ClassicEditor
  const feedbackFieldId = formId + '-feedback'

  const translated = {
    status: django.gettext('Processing status'),
    noStatus: django.gettext('No processing status'),
    feedback: django.gettext('Official feedback'),
    charCount: django.gettext(' characters'),
    cancel: django.gettext('Cancel'),
    submit: django.gettext('Submit feedback'),
    submitEdit: django.gettext('Update feedback')
  }

  const parseConfig = () => {
    if (!props.ckeditorConfig) return {}
    try {
      return JSON.parse(props.ckeditorConfig)
    } catch (error) {
      console.warn(error)
      return {}
    }
  }

  useEffect(() => {
    const container = editorContainerRef.current
    if (!container || !window.ClassicEditor) return

    let isCancelled = false
    let editor: any = null

    // The editor is created in its own element so React never has to
    // reconcile CKEditor's DOM.
    const editorElement = document.createElement('div')
    editorElement.className = 'ck-editor-container'
    container.appendChild(editorElement)

    const setupEditor = async () => {
      try {
        const createdEditor = await window.ClassicEditor.create(editorElement, {
          ...parseConfig(),
          initialData: initialFeedback?.feedback_text || ''
        })
        if (isCancelled) {
          await createdEditor.destroy().catch(() => {})
          editorElement.remove()
          return
        }
        editor = createdEditor
        const editableElement = createdEditor.ui.getEditableElement()
        if (editableElement) {
          editableElement.setAttribute('id', feedbackFieldId)
          editableElement.setAttribute('aria-label', translated.feedback)
        }
        createdEditor.model.document.on('change:data', () => {
          if (!isCancelled) {
            setFeedback(createdEditor.getData())
          }
        })
      } catch (error) {
        console.warn(error)
        editorElement.remove()
      }
    }
    setupEditor()

    return () => {
      isCancelled = true
      if (editor) {
        try {
          editor.destroy().catch((error: unknown) => console.warn(error))
        } catch (error) {
          console.warn(error)
        }
        editorElement.remove()
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (isSubmitting) return
    setIsSubmitting(true)
    try {
      await props.onSubmit({
        feedback,
        status: status || null
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const charCount = plainTextLength(feedback)
  const overLimit = charCount > FEEDBACK_MAX_LENGTH

  return (
    <form className="general-form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor={formId + '-status'}>{translated.status}</label>
        <select
          className="form-select"
          id={formId + '-status'}
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        >
          <option value="">{translated.noStatus}</option>
          {(item.moderator_status_choices || []).map(choice => (
            <option key={choice.value} value={choice.value}>{choice.label}</option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label htmlFor={feedbackFieldId}>{translated.feedback}</label>
        {supportsRichText
          ? <div ref={editorContainerRef} />
          : (
            <textarea
              id={feedbackFieldId}
              className="form-control"
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
            />
            )}
      </div>

      <div className="row align-items-center">
        <span className="col-6 a4-comments__char-count">
          {charCount}/{FEEDBACK_MAX_LENGTH}{translated.charCount}
        </span>
        <div className="a4-comments__submit d-flex col-6 justify-content-end">
          <button
            type="button"
            className="btn btn--secondary me-2"
            onClick={props.onCancel}
          >
            {translated.cancel}
          </button>
          <button
            type="submit"
            className="btn btn--default a4-comments__submit-input"
            disabled={isSubmitting || overLimit}
          >
            {initialFeedback ? translated.submitEdit : translated.submit}
          </button>
        </div>
      </div>
    </form>
  )
}
