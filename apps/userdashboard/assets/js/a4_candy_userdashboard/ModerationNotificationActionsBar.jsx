import React from 'react'
import django from 'django'
import { HoverButton } from '../../../../../apps/contrib/assets/HoverButton'

export const ModerationNotificationActionsBar = (props) => {
  const translated = {
    blockText: django.pgettext('kosmo', 'Block'),
    unblockText: django.pgettext('kosmo', 'Unblock'),
    isBlockedText: django.pgettext('kosmo', 'Blocked'),
    replyText: django.pgettext('kosmo', 'Add feedback'),
    blockedText: django.pgettext('kosmo', 'This comment was blocked'),
    highlightText: django.pgettext('kosmo', 'Highlight'),
    unhighlightText: django.pgettext('kosmo', 'Unhighlight'),
    isHighlightedText: django.pgettext('kosmo', 'Highlighted'),
    unarchiveText: django.pgettext('kosmo', 'Unarchive'),
    archivedText: django.pgettext('kosmo', 'Archived'),
    editText: django.pgettext('kosmo', 'Edit feedback')
  }

  const {
    isPending,
    isEditing,
    isBlocked,
    isHighlighted,
    onToggleForm,
    onToggleBlock,
    onToggleHighlight,
    onTogglePending
  } = props

  return isPending
    ? (
      <div className="my-3 d-flex flex-wrap justify-content-between">
        <button
          id="moderation-notification-actions-bar-button-reply"
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
            id="moderation-notification-actions-bar-button-highlight"
            className="btn userdashboard-mod-notification__btn"
            onClick={onToggleHighlight}
            disabled={isBlocked}
            icon={<i className="icon-fo-highlight" aria-hidden="true" />}
            textMouseOff={isHighlighted ? translated.isHighlightedText : translated.highlightText}
            textMouseOn={isHighlighted ? translated.unhighlightText : translated.highlightText}
          />
          <HoverButton
            id="moderation-notification-actions-bar-button-block"
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
    : (
      <div className={'my-3 d-flex justify-content-' + (!isBlocked ? 'end' : 'between')}>
        {isBlocked &&
          <div className="fw-bold">
            <i className="fas fa-exclamation-circle me-1" aria-hidden="true" />
            {translated.blockedText}
          </div>}
        <HoverButton
          id="moderation-notification-actions-bar-button-pending"
          className="btn userdashboard-mod-notification__btn"
          onClick={onTogglePending}
          icon={<i className="fas fa-archive me-1" aria-hidden="true" />}
          textMouseOn={translated.unarchiveText}
          textMouseOff={translated.archivedText}
        />
      </div>
      )
}
