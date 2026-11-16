import React from 'react'
import django from 'django'

interface ModerationNotificationActionsBarProps {
  isEditing?: boolean
  isBlocked?: boolean
  isHighlighted?: boolean
  isUnread?: boolean
  itemPk?: number
  showModerationActions?: boolean
  onToggleForm?: (isEditing: boolean) => void
  onToggleBlock?: () => void
  onToggleHighlight?: () => void
  onMarkResolved?: () => void
  onReopen?: () => void
}

export const ModerationNotificationActionsBar = (props: ModerationNotificationActionsBarProps) => {
  const translated = {
    giveFeedback: django.gettext('Give feedback'),
    editFeedback: django.gettext('Edit feedback'),
    markResolved: django.gettext('Mark as resolved'),
    highlight: django.gettext('Highlight comment'),
    hide: django.gettext('Hide from discussion'),
    reopen: django.gettext('Reopen report')
  }

  const {
    isEditing,
    isBlocked,
    isHighlighted,
    isUnread = true,
    itemPk,
    showModerationActions = true,
    onToggleForm,
    onToggleBlock,
    onToggleHighlight,
    onMarkResolved,
    onReopen
  } = props

  if (isBlocked) {
    return (
      <div className="userdashboard-mod-actions">
        <div className="userdashboard-mod-actions__right">
          <button
            id={'moderation-notification-actions-bar-button-reopen-' + itemPk}
            className="btn btn--none userdashboard-mod-actions__btn"
            type="button"
            onClick={onReopen}
          >
            <i className="fas fa-arrow-rotate-left" aria-hidden="true" />
            <span className="ms-2">{translated.reopen}</span>
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="userdashboard-mod-actions">
      <button
        id={'moderation-notification-actions-bar-button-reply-' + itemPk}
        className="btn btn--none userdashboard-mod-actions__btn"
        type="button"
        onClick={() => onToggleForm?.(!!isEditing)}
      >
        <i
          className={isEditing ? 'fas fa-pen' : 'fas fa-reply'}
          aria-hidden="true"
        />
        <span className="ms-2">
          {isEditing ? translated.editFeedback : translated.giveFeedback}
        </span>
      </button>
      <div className="userdashboard-mod-actions__right">
        {isUnread &&
          <button
            id={'moderation-notification-actions-bar-button-resolve-' + itemPk}
            className="btn btn--none userdashboard-mod-actions__btn"
            type="button"
            onClick={onMarkResolved}
          >
            <i className="fas fa-box-archive" aria-hidden="true" />
            <span className="ms-2">{translated.markResolved}</span>
          </button>}
        {showModerationActions && (isHighlighted
          ? (
            <button
              id={'moderation-notification-actions-bar-button-block-' + itemPk}
              className="btn btn--none userdashboard-mod-actions__btn userdashboard-mod-actions__btn--danger"
              type="button"
              onClick={onToggleBlock}
            >
              <i className="fas fa-eye-slash" aria-hidden="true" />
              <span className="ms-2">{translated.hide}</span>
            </button>
            )
          : (
            <button
              id={'moderation-notification-actions-bar-button-highlight-' + itemPk}
              className="btn btn--none userdashboard-mod-actions__btn userdashboard-mod-actions__btn--primary"
              type="button"
              onClick={onToggleHighlight}
            >
              <i className="fas fa-highlighter" aria-hidden="true" />
              <span className="ms-2">{translated.highlight}</span>
            </button>
            ))}
      </div>
    </div>
  )
}
