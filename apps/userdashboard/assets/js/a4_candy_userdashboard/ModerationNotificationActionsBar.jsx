import React from 'react'
import django from 'django'
import { HoverButton } from '../../../../../apps/contrib/assets/HoverButton'

export const ModerationNotificationActionsBar = (props) => {
  const translated = {
    blockText: django.gettext('Block'),
    unblockText: django.gettext('Unblock'),
    isBlockedText: django.gettext('Blocked'),
    replyText: django.gettext('Add feedback'),
    blockedText: django.gettext('This comment was blocked'),
    highlightText: django.gettext('Highlight'),
    unhighlightText: django.gettext('Unhighlight'),
    isHighlightedText: django.gettext('Highlighted'),
    unreadText: django.gettext('Unread'),
    readText: django.gettext('Read'),
    editText: django.gettext('Edit feedback')
  }

  const {
    isEditing,
    isBlocked,
    isHighlighted,
    itemPk,
    onToggleForm,
    onToggleBlock,
    onToggleHighlight
  } = props

  return (
    <div className="d-flex flex-wrap justify-content-between">
      <button
        id={'moderation-notification-actions-bar-button-reply-' + itemPk}
        className="btn px-0 userdashboard-mod-notification__btn"
        type="button"
        onClick={() => onToggleForm(!!isEditing)}
      >
        {isEditing
          ? <i className="fas fa-pen" aria-hidden="true" />
          : <i className="fas fa-reply" aria-hidden="true" />}
        {isEditing
          ? <span className="ms-2">{translated.editText}</span>
          : <span className="ms-2">{translated.replyText}</span>}
      </button>
      <div>
        <HoverButton
          id={'moderation-notification-actions-bar-button-highlight-' + itemPk}
          className="btn userdashboard-mod-notification__btn"
          onClick={onToggleHighlight}
          disabled={isBlocked}
          icon={<i className="fas fa-highlighter" aria-hidden="true" />}
          textMouseOff={isHighlighted ? translated.isHighlightedText : translated.highlightText}
          textMouseOn={isHighlighted ? translated.unhighlightText : translated.highlightText}
        />
        <HoverButton
          id={'moderation-notification-actions-bar-button-block-' + itemPk}
          className="btn userdashboard-mod-notification__btn"
          onClick={onToggleBlock}
          disabled={isHighlighted}
          icon={<i className="fas fa-ban" aria-hidden="true" />}
          textMouseOff={isBlocked ? translated.isBlockedText : translated.blockText}
          textMouseOn={isBlocked ? translated.unblockText : translated.blockText}
        />
      </div>
    </div>
  )
}
