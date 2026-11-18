import React, { useRef, useState } from 'react'
import django from 'django'
import api from './api'
import { ModerationFeedback } from './ModerationFeedback'
import { ModerationFeedbackEditorForm } from './ModerationFeedbackEditorForm'
import { ModerationNotificationActionsBar } from './ModerationNotificationActionsBar'
import { alert as Alert } from 'adhocracy4'
import type { ModerationItem } from './types'

const alertTime = 6000

const translated = {
  feedbackAdded: django.gettext('Your feedback was successfully delivered.'),
  feedbackEdited: django.gettext('Your feedback was successfully updated.'),
  feedbackDeleted: django.gettext('Your feedback was successfully deleted.'),
  anotherFeedback: django.gettext('The comment has already been moderated. Your feedback could not be saved.'),
  goToDiscussion: django.gettext('Go to discussion'),
  commentBlocked: django.gettext('Comment blocked successfully.'),
  commentUnblocked: django.gettext('Comment unblocked successfully.'),
  commentHighlighted: django.gettext('Comment highlighted successfully.'),
  commentUnhighlighted: django.gettext('Comment unhighlighted successfully.'),
  notificationRead: django.gettext('Notification successfully marked as read.'),
  notificationUnread: django.gettext('Notification successfully marked as unread.'),
  hiddenFromDiscussion: django.gettext('Hidden from discussion by Moderator'),
  aiClassified: django.gettext('AI'),
  postedComment: django.gettext('posted a {}comment{}'),
  submittedIdea: django.gettext('submitted the idea at'),
  commentedOn: django.gettext('commented on'),
  project: django.gettext('the project'),
  statusSaved: django.gettext('Processing status saved.'),
  readMore: django.gettext('Read more'),
  showLess: django.gettext('Show less'),
  imagePreview: django.gettext('Image preview'),
  close: django.gettext('Close'),
  saveFailed: django.gettext('Your changes could not be saved. Please try again.')
}

interface AlertValue {
  type: string
  message: React.ReactNode
  timeInMs?: number
}

interface ModerationNotificationProps {
  notification: ModerationItem
  apiUrl?: string
  getUrlParams?: () => string
  loadData?: () => void
  onChangeStatus?: (error: unknown) => void
  ckeditorConfig?: string
  projectTitle?: string
  projectUrl?: string
}

export const ModerationNotification = (props: ModerationNotificationProps) => {
  const { notification, projectTitle, projectUrl } = props
  const isIdea = notification.item_type === 'idea'
  const [showFeedbackForm, setShowFeedbackForm] = useState(false)
  const [showFullText, setShowFullText] = useState(false)
  const [alert, setAlert] = useState<AlertValue>()
  const imageDialogRef = useRef<HTMLDialogElement>(null)
  const imageButtonRef = useRef<HTMLButtonElement>(null)

  function getLink (string: string, url: string) {
    const splitted = string.split('{}')
    return (
      <span>
        {splitted[0]}
        <a target="_blank" rel="noreferrer" href={url}>{splitted[1]}</a>
        {splitted[2]}
      </span>
    )
  }

  // Return a react component to render the anchor, we should probably rather
  // extent the Alert component to handle
  function getFeedbackAdded (commentUrl?: string) {
    return (
      <>
        {translated.feedbackAdded} {commentUrl && <a href={commentUrl}>{translated.goToDiscussion}</a>}
      </>
    )
  }

  // **** Start feedback methods ****

  const feedbackDetailUrl = () => {
    if (isIdea) {
      return notification.feedback_api_url
    }
    return notification.feedback_api_url + notification.moderator_feedback?.pk + '/'
  }

  const handleFeedbackSubmit = async (payload: string, markResolved: boolean) => {
    const [getResponse] = await api.fetch<any[]>({
      url: notification.feedback_api_url,
      method: 'GET'
    })

    if (getResponse && getResponse.length > 0) {
      setShowFeedbackForm(false)
      setAlert({
        type: 'error',
        message: translated.anotherFeedback,
        timeInMs: alertTime
      })
    } else {
      const [, error] = await api.fetch({
        url: notification.feedback_api_url,
        method: 'POST',
        body: { feedback_text: payload, mark_resolved: markResolved }
      })
      if (error) {
        setAlert({
          type: 'error',
          message: String(error),
          timeInMs: alertTime
        })
      } else {
        props.loadData?.()
        setShowFeedbackForm(false)
        setAlert({
          type: 'success',
          message: getFeedbackAdded(),
          timeInMs: alertTime
        })
      }
    }
  }

  const handleFeedbackEdit = async (payload: string, markResolved: boolean) => {
    const [, error] = await api.fetch({
      url: feedbackDetailUrl(),
      method: 'PUT',
      body: { feedback_text: payload, mark_resolved: markResolved }
    })
    if (error) {
      props.onChangeStatus?.(error)
    } else {
      props.loadData?.()
      setShowFeedbackForm(false)
      setAlert({
        type: 'success',
        message: translated.feedbackEdited,
        timeInMs: alertTime
      })
    }
  }

  const handleFeedbackDelete = async () => {
    const [, error] = await api.fetch({
      url: feedbackDetailUrl(),
      method: 'DELETE'
    })
    if (error) {
      setAlert({
        type: 'error',
        message: translated.saveFailed,
        timeInMs: alertTime
      })
      return
    }
    props.loadData?.()
    setShowFeedbackForm(false)
    setAlert({
      type: 'success',
      message: translated.feedbackDeleted,
      timeInMs: alertTime
    })
  }

  const handleIdeaFeedbackSubmit = async (payload: { feedback: string, status: string | null, markResolved: boolean }) => {
    const currentFeedback = notification.moderator_feedback?.feedback_text || ''
    const statusChanged = payload.status !== (notification.moderator_status || null)
    const feedbackChanged = payload.feedback !== currentFeedback
    const clearFeedback = feedbackChanged &&
      payload.feedback.trim() === '' &&
      !!notification.moderator_feedback

    if (!feedbackChanged && !statusChanged) {
      setShowFeedbackForm(false)
      return
    }

    let error: unknown
    let alertMessage = translated.statusSaved

    if (clearFeedback) {
      const [, deleteError] = await api.fetch({
        url: notification.feedback_api_url,
        method: 'DELETE'
      })
      error = deleteError
      alertMessage = translated.feedbackDeleted
      if (!deleteError && statusChanged) {
        const [, statusError] = await api.fetch({
          url: notification.api_url,
          method: 'PATCH',
          body: { moderator_status: payload.status }
        })
        error = statusError
      }
    } else if (feedbackChanged) {
      const [, feedbackError] = await api.fetch({
        url: notification.feedback_api_url,
        method: notification.moderator_feedback ? 'PUT' : 'POST',
        body: {
          feedback_text: payload.feedback,
          mark_resolved: payload.markResolved,
          ...(statusChanged ? { moderator_status: payload.status } : {})
        }
      })
      error = feedbackError
      alertMessage = notification.moderator_feedback
        ? translated.feedbackEdited
        : translated.feedbackAdded
    } else if (statusChanged) {
      const [, statusError] = await api.fetch({
        url: notification.api_url,
        method: 'PATCH',
        body: { moderator_status: payload.status }
      })
      error = statusError
      if (!statusError && payload.markResolved && notification.is_unread) {
        await api.fetch({
          url: (props.apiUrl || '') + 'mark_read/' + (props.getUrlParams?.() || ''),
          method: 'GET'
        })
      }
    }

    if (error) {
      setAlert({
        type: 'error',
        message: String(error) || translated.saveFailed,
        timeInMs: alertTime
      })
    } else {
      props.loadData?.()
      setShowFeedbackForm(false)
      setAlert({
        type: 'success',
        message: alertMessage,
        timeInMs: alertTime
      })
    }
  }

  function toggleModerationFeedbackForm () {
    setShowFeedbackForm(!showFeedbackForm)
  }

  function hideFromDiscussion () {
    setShowFeedbackForm(false)
    toggleIsBlocked()
  }

  // **** End feedback methods ****

  // **** Start notification methods ****

  async function toggleIsUnread () {
    const action = notification.is_unread ? 'mark_read/' : 'mark_unread/'
    const url = (props.apiUrl || '') + action + (props.getUrlParams?.() || '')
    const [response, error] =
      await api.fetch<any>({
        url,
        method: 'GET'
      })
    const alertMessage = response && response.is_unread
      ? translated.notificationUnread
      : translated.notificationRead

    if (error) {
      setAlert({
        type: 'error',
        message: String(error),
        timeInMs: alertTime
      })
    } else {
      props.loadData?.()
      setAlert({
        type: 'success',
        message: alertMessage,
        timeInMs: alertTime
      })
    }
  }

  async function markResolved () {
    const [, error] = await api.fetch<any>({
      url: (props.apiUrl || '') + 'mark_read/' + (props.getUrlParams?.() || ''),
      method: 'GET'
    })
    if (error) {
      setAlert({
        type: 'error',
        message: String(error),
        timeInMs: alertTime
      })
    } else {
      props.loadData?.()
      setAlert({
        type: 'success',
        message: translated.notificationRead,
        timeInMs: alertTime
      })
    }
  }

  async function toggleIsBlocked () {
    const [response, error] =
      await api.fetch<any>({
        url: (props.apiUrl || '') + (props.getUrlParams?.() || ''),
        method: 'PATCH',
        body: { is_blocked: !notification.is_blocked }
      })
    const alertMessage = response && response.is_blocked
      ? translated.commentBlocked
      : translated.commentUnblocked

    if (error) {
      setAlert({
        type: 'error',
        message: String(error),
        timeInMs: alertTime
      })
    } else {
      props.loadData?.()
      setAlert({
        type: 'success',
        message: alertMessage,
        timeInMs: alertTime
      })
    }
  }

  async function toggleIsHighlighted () {
    const [response, error] =
      await api.fetch<any>({
        url: (props.apiUrl || '') + (props.getUrlParams?.() || ''),
        method: 'PATCH',
        body: { is_moderator_marked: !notification.is_moderator_marked }
      })
    const alertMessage = response && response.is_moderator_marked
      ? translated.commentHighlighted
      : translated.commentUnhighlighted

    if (error) {
      setAlert({
        type: 'error',
        message: String(error),
        timeInMs: alertTime
      })
    } else {
      props.loadData?.()
      setAlert({
        type: 'success',
        message: alertMessage,
        timeInMs: alertTime
      })
    }
  }

  // **** End notification methods ****

  function translatedReportText (reportsFound: number, isIdeaItem: boolean) {
    const tmp = isIdeaItem
      ? django.ngettext(
        'This {}idea{} has been reported 1 time since it\'s creation',
        'This {}idea{} has been reported %s times since it\'s creation',
        reportsFound
      )
      : django.ngettext(
        'This {}comment{} has been reported 1 time since it\'s creation',
        'This {}comment{} has been reported %s times since it\'s creation',
        reportsFound
      )
    return django.interpolate(tmp, [reportsFound])
  }

  const {
    text: itemText,
    text_preview: itemTextPreview,
    image: itemImage,
    url: itemUrl,
    last_edit: created,
    is_modified: isModified,
    user_image: userImage,
    user_name: userName,
    user_profile_url: userProfileUrl,
    num_reports: numReports,
    title: ideaTitle
  } = notification
  const markReadText = django.gettext('Mark as read')
  const markUnreadText = django.gettext('Mark as unread')

  let userImageDiv
  if (userImage) {
    const sectionStyle = {
      backgroundImage: 'url(' + userImage + ')'
    }
    userImageDiv = <div className="col-4 user-avatar user-avatar--small user-avatar--shadow mb-1 userindicator__btn-img" style={sectionStyle} />
  }

  let commentChangeLog
  if (isModified) {
    commentChangeLog = django.gettext('Last edited on ' + created)
  } else {
    commentChangeLog = django.gettext('Created on ' + created)
  }

  function getByline () {
    const projectLink = projectUrl && projectTitle
      ? <a href={projectUrl}>{projectTitle}</a>
      : null
    if (isIdea) {
      return (
        <>
          <i className="fas fa-lightbulb me-1" aria-hidden="true" />
          {userProfileUrl ? <a href={userProfileUrl}>{userName}</a> : userName}{' '}
          {translated.submittedIdea}{' '}
          {projectLink || <a href={itemUrl}>{ideaTitle}</a>}
        </>
      )
    }
    return (
      <>
        <i className="far fa-comment me-1" aria-hidden="true" />
        {userProfileUrl ? <a href={userProfileUrl}>{userName}</a> : userName}{' '}
        {translated.commentedOn}{' '}
        {projectLink || <a href={itemUrl}>{translated.project}</a>}
      </>
    )
  }

  function openImagePreview () {
    imageDialogRef.current?.showModal()
  }

  function closeImagePreview () {
    imageDialogRef.current?.close()
  }

  const displayedText = isIdea && !showFullText && itemTextPreview
    ? itemTextPreview
    : itemText

  const ideaTextId = 'moderation-idea-text-' + notification.pk
  const imagePreviewLabel = ideaTitle
    ? django.interpolate(django.gettext('Image preview: {}'), [ideaTitle])
    : translated.imagePreview

  const labelClass = 'userdashboard-mod-item__label userdashboard-mod-item__label--' + notification.item_type

  return (
    <li>
      <div className="u-border p-4 userdashboard-mod-item__card">
        <div className="d-flex flex-wrap">
          {userImageDiv}
          <div className="col-6 d-none d-md-block">
            <p className="mb-1">
              {getByline()}
            </p>
            <p className="mb-1">{commentChangeLog}</p>
          </div>
          <div className="col-auto ms-auto">
            <div className="dropdown">
              <button
                title="{% trans 'Notification menu' %}"
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
                    onClick={() => toggleIsUnread()}
                  >
                    {notification.is_unread ? markReadText : markUnreadText}
                  </button>
                </li>
              </ul>
            </div>
          </div>
          <div className="col-12 d-md-none">
            <p className="mb-1">
              {getByline()}
            </p>
            <p className="mb-1">{commentChangeLog}</p>
          </div>
        </div>

        <span className={labelClass}>{notification.label}</span>

        {isIdea && notification.moderator_status &&
          <span className={'userdashboard-mod-item__label userdashboard-mod-item__status userdashboard-mod-item__status--' + notification.moderator_status.toLowerCase()}>
            {notification.moderator_status_display}
          </span>}

        {numReports > 0 &&
          <div>
            <p>
              <i className="fas fa-exclamation-circle me-1" aria-hidden="true" />
              {getLink(translatedReportText(numReports, isIdea), itemUrl)}
            </p>
          </div>}

        {isIdea
          ? (
            <>
              <div
                id={ideaTextId}
                className="ck-content userdashboard-mod-item__text"
                aria-live="polite"
                dangerouslySetInnerHTML={{ __html: displayedText }}
              />
              {itemTextPreview &&
                <button
                  type="button"
                  className="btn btn--none px-0 userdashboard-mod-item__text-toggle"
                  aria-expanded={showFullText}
                  aria-controls={ideaTextId}
                  onClick={() => setShowFullText(!showFullText)}
                >
                  {showFullText ? translated.showLess : translated.readMore}
                </button>}
            </>
            )
          : <p>{itemText}</p>}

        {isIdea && itemImage &&
          <>
            <button
              ref={imageButtonRef}
              type="button"
              className="userdashboard-mod-item__image-btn"
              onClick={openImagePreview}
              aria-haspopup="dialog"
              aria-label={imagePreviewLabel}
            >
              <img
                className="userdashboard-mod-item__image"
                src={itemImage.thumbnail}
                alt=""
              />
            </button>
            <dialog
              ref={imageDialogRef}
              className="a4-modal userdashboard-mod-item__image-modal"
              aria-label={imagePreviewLabel}
              onClose={() => imageButtonRef.current?.focus()}
            >
              <div className="a4-modal__content">
                <header className="a4-modal__header">
                  <button
                    className="a4-modal__close"
                    aria-label={translated.close}
                    onClick={closeImagePreview}
                    type="button"
                  >
                    <i className="fa fa-times" aria-hidden="true" />
                  </button>
                </header>
                <div className="a4-modal__body">
                  <img src={itemImage.full} alt={ideaTitle || ''} />
                </div>
              </div>
            </dialog>
          </>}

        {notification.is_blocked &&
          <div className="userdashboard-mod-item__hidden">
            <i className="far fa-eye-slash me-1" aria-hidden="true" />
            <span>{translated.hiddenFromDiscussion} · {created}</span>
          </div>}

        {!notification.is_blocked && notification.moderator_feedback && !showFeedbackForm &&
          <ModerationFeedback feedback={notification.moderator_feedback} />}

        <ModerationNotificationActionsBar
          itemPk={notification.pk}
          itemType={notification.item_type}
          isEditing={!!notification.moderator_feedback}
          isBlocked={notification.is_blocked}
          isHighlighted={notification.is_moderator_marked}
          isUnread={notification.is_unread}
          showModerationActions={!isIdea}
          onToggleForm={() => toggleModerationFeedbackForm()}
          onToggleBlock={() => hideFromDiscussion()}
          onToggleHighlight={() => toggleIsHighlighted()}
          onMarkResolved={() => markResolved()}
          onReopen={() => toggleIsBlocked()}
        />
        {showFeedbackForm &&
          <ModerationFeedbackEditorForm
            key={notification.moderator_feedback?.pk || 'new'}
            item={notification}
            initialFeedback={notification.moderator_feedback}
            ckeditorConfig={props.ckeditorConfig}
            showStatus={isIdea}
            onSubmit={(payload) => {
              if (isIdea) {
                return handleIdeaFeedbackSubmit(payload)
              }
              if (notification.moderator_feedback) {
                return handleFeedbackEdit(payload.feedback, payload.markResolved)
              }
              return handleFeedbackSubmit(payload.feedback, payload.markResolved)
            }}
            onCancel={() => {
              setShowFeedbackForm(false)
            }}
            onDelete={notification.moderator_feedback ? handleFeedbackDelete : undefined}
          />}
      </div>
      <div className="mb-3">
        <Alert {...alert} onClick={() => setAlert(undefined)} />
      </div>
    </li>
  )
}
