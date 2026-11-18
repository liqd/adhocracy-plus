import React from 'react'
import django from 'django'
import type { ModeratorFeedback } from './types'
import { ReplyOutlineIcon } from './ReplyOutlineIcon'

interface ModerationFeedbackProps {
  feedback: ModeratorFeedback
}

export const ModerationFeedback = ({ feedback }: ModerationFeedbackProps) => {
  const translated = {
    title: django.gettext('Moderator')
  }

  return (
    <div className="userdashboard-mod-feedback">
      <div className="userdashboard-mod-feedback__header">
        <span className="me-2"><ReplyOutlineIcon /></span>
        <span className="userdashboard-mod-feedback__title">{translated.title}</span>
      </div>
      <p className="userdashboard-mod-feedback__date mb-2">{feedback.last_edit}</p>
      <div
        className="userdashboard-mod-feedback__text ck-content"
        dangerouslySetInnerHTML={{ __html: feedback.feedback_text }}
      />
    </div>
  )
}
