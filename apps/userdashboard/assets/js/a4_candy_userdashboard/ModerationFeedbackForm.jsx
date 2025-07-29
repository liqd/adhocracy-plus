import React, { useState } from 'react'
import django from 'django'

const MODERATOR_FEEDBACK_MAX_LENGTH = 500

export const ModerationFeedbackForm = (props) => {
  const [feedback, setFeedback] =
    useState((props.editing && props.initialFeedback.feedback_text) || '')

  const translated = {
    placeholder: django.gettext('Write feedback'),
    charCount: django.gettext(' characters'),
    submitLabel: django.gettext('submit feedback'),
    submitEditLabel: django.gettext('update feedback')
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (props.editing) {
      props.onEditSubmit(feedback)
    } else {
      props.onSubmit(feedback)
    }
  }

  return (
    <form className="general-form" onSubmit={handleSubmit}>
      <textarea
        className="a4-comments__textarea--small form-group"
        placeholder={translated.placeholder}
        onChange={(e) => setFeedback(e.target.value)}
        value={feedback}
        maxLength={MODERATOR_FEEDBACK_MAX_LENGTH}
      />
      <div className="row">
        <label htmlFor="id-comment-form" className="col-6 a4-comments__char-count">
          {feedback.length}/{MODERATOR_FEEDBACK_MAX_LENGTH}{translated.charCount}
        </label>
        <div className="a4-comments__submit d-flex col-6">
          <button
            type="submit"
            className="btn btn--default a4-comments__submit-input ms-auto"
          >
            {props.editing ? translated.submitEditLabel : translated.submitLabel}
          </button>
        </div>
      </div>
    </form>
  )
}
