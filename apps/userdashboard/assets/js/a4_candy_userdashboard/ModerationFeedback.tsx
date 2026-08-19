import React from 'react'
import django from 'django'
import type { ModeratorFeedback } from './types'

interface ModerationFeedbackProps {
  feedback: ModeratorFeedback
  onDelete?: (pk: number) => void
  onEdit?: () => void
}

export const ModerationFeedback = ({ feedback, onDelete, onEdit }: ModerationFeedbackProps) => {
  const { feedback_text: feedbackText, last_edit: lastEdit, pk } = feedback
  const translated = {
    delete: django.gettext('delete'),
    edit: django.gettext('edit'),
    feedbackTitle: django.gettext('Moderator\'s feedback'),
    editWasOn: django.gettext('Last edit was on ')
  }

  return (
    <div className="userdashboard-mod-feedback">
      <div className="row">
        <div className="col-7 col-md-8 userdashboard-mod-feedback__header">
          <div>{translated.feedbackTitle}</div>
        </div>
        <div className="col">
          <div className="text-end">
            <div className="dropdown">
              <button
                title="{% trans 'Feedback menu' %}"
                type="button"
                className="dropdown-toggle btn btn--none"
                aria-haspopup="true"
                aria-expanded="false"
                data-bs-toggle="dropdown"
              >
                <i className="fas fa-ellipsis-v" aria-hidden="true" />
              </button>
              <ul className="dropdown-menu dropdown-menu-end">
                <li key="1">
                  <button
                    className="dropdown-item"
                    type="button"
                    id="delete-input"
                    onClick={() => onDelete?.(pk)}
                  >
                    {translated.delete}
                  </button>
                </li>
                <li key="2">
                  <button
                    className="dropdown-item"
                    type="button"
                    id="edit-input"
                    onClick={onEdit}
                  >
                    {translated.edit}
                  </button>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      <div className="row">
        <div className="col">
          <p>
            {translated.editWasOn}{lastEdit}
          </p>
        </div>
      </div>
      <div className="row">
        <div className="col-12">
          <span className="userdashboard-mod-feedback__text">{feedbackText}</span>
        </div>
      </div>
    </div>
  )
}
