import React, { useState } from 'react'
import django from 'django'
import api from './api'
import { ModerationFeedbackForm } from './ModerationFeedbackForm'
import { ModerationFeedback } from './ModerationFeedback'
import { ModerationNotificationActionsBar } from './ModerationNotificationActionsBar'
import { alert as Alert } from 'adhocracy4'

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
  aiClassified: django.gettext('AI'),
  postedComment: django.gettext('posted a {}comment{}')
}

export const ModerationNotification = (props) => {
  const { notification } = props
  const [showFeedbackForm, setShowFeedbackForm] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [alert, setAlert] = useState()

  function getLink (string, url) {
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
  function getFeedbackAdded (commentUrl) {
    return (
      <>
        {translated.feedbackAdded} <a href={commentUrl}>{translated.goToDiscussion}</a>
      </>
    )
  }

  // **** Start feedback methods ****

  const handleFeedbackSubmit = async (payload) => {
    const [getResponse] = await api.fetch({
      url: notification.feedback_api_url,
      method: 'GET'
    })

    if (getResponse.length > 0) {
      setShowFeedbackForm(false)
      setAlert({
        type: 'error',
        message: translated.anotherFeedback,
        timeInMs: alertTime
      })
    } else {
      // eslint-disable-next-line no-unused-vars
      const [response, error] = await api.fetch({
        url: notification.feedback_api_url,
        method: 'POST',
        body: { feedback_text: payload }
      })
      if (error) {
        setAlert({
          type: 'error',
          message: error,
          timeInMs: alertTime
        })
      } else {
        props.loadData()
        setShowFeedbackForm(false)
        setAlert({
          type: 'success',
          message: getFeedbackAdded(),
          timeInMs: alertTime
        })
      }
    }
  }

  const handleFeedbackEdit = async (payload) => {
    // eslint-disable-next-line no-unused-vars
    const [response, error] = await api.fetch({
      url: notification.feedback_api_url + notification.moderator_feedback.pk + '/',
      method: 'PUT',
      body: { feedback_text: payload }
    })
    if (error) {
      props.onChangeStatus(error)
    } else {
      props.loadData()
      setShowFeedbackForm(false)
      setIsEditing(false)
      setAlert({
        type: 'success',
        message: translated.feedbackEdited,
        timeInMs: alertTime
      })
    }
  }

  const handleFeedbackDelete = async () => {
    await api.fetch({
      url: notification.feedback_api_url + notification.moderator_feedback.pk + '/',
      method: 'DELETE'
    })
    props.loadData()
    setAlert({
      type: 'success',
      message: translated.feedbackDeleted,
      timeInMs: alertTime
    })
  }

  function toggleModerationFeedbackForm (isEditing) {
    isEditing && setIsEditing(true)
    setShowFeedbackForm(!showFeedbackForm)
  }

  // **** End feedback methods ****

  // **** Start notification methods ****

  async function toggleIsUnread () {
    const url = notification.is_unread
      ? props.apiUrl + 'mark_read/' + props.getUrlParams()
      : props.apiUrl + 'mark_unread/' + props.getUrlParams()
    const [response, error] =
      await api.fetch({
        url,
        method: 'GET'
      })
    const alertMessage = response && response.is_unread
      ? translated.notificationUnread
      : translated.notificationRead

    if (error) {
      setAlert({
        type: 'error',
        message: error,
        timeInMs: alertTime
      })
    } else {
      setAlert({
        type: 'success',
        message: alertMessage,
        timeInMs: alertTime
      })
    }
  }

  async function toggleIsBlocked () {
    const [response, error] =
      await api.fetch({
        url: props.apiUrl + props.getUrlParams(),
        method: 'PATCH',
        body: { is_blocked: !notification.is_blocked }
      })
    const alertMessage = response && response.is_blocked
      ? translated.commentBlocked
      : translated.commentUnblocked

    if (error) {
      setAlert({
        type: 'error',
        message: error,
        timeInMs: alertTime
      })
    } else {
      setAlert({
        type: 'success',
        message: alertMessage,
        timeInMs: alertTime
      })
    }
  }

  async function toggleIsHighlighted () {
    const [response, error] =
      await api.fetch({
        url: props.apiUrl + props.getUrlParams(),
        method: 'PATCH',
        body: { is_moderator_marked: !notification.is_moderator_marked }
      })
    const alertMessage = response && response.is_moderator_marked
      ? translated.commentHighlighted
      : translated.commentUnhighlighted

    if (error) {
      setAlert({
        type: 'error',
        message: error,
        timeInMs: alertTime
      })
    } else {
      setAlert({
        type: 'success',
        message: alertMessage,
        timeInMs: alertTime
      })
    }
  }

  // **** End notification methods ****

  function translatedReportText (reportsFound) {
    const tmp = django.ngettext(
      '\'s {}comment{} has been reported 1 time since it\'s creation',
      '\'s {}comment{} has been reported %s times since it\'s creation',
      reportsFound
    )
    return (
      django.interpolate(tmp, [reportsFound])
    )
  }

  const {
    comment: commentText,
    comment_url: commentUrl,
    last_edit: created,
    is_modified: isModified,
    user_image: userImage,
    user_name: userName,
    user_profile_url: userProfileUrl,
    num_reports: numReports
  } = notification
  const markReadText = django.gettext('Mark as read')
  const markUnreadText = django.gettext('Mark as unread')

  let userImageDiv
  if (userImage) {
    const sectionStyle = {
      backgroundImage: 'url(' + userImage + ')'
    }
    userImageDiv = <div className="user-avatar user-avatar--small user-avatar--shadow mb-1 userindicator__btn-img" style={sectionStyle} />
  }

  let commentChangeLog
  if (isModified) {
    commentChangeLog = django.gettext('Last edited on ' + created)
  } else {
    commentChangeLog = django.gettext('Created on ' + created)
  }

  return (
    <li>
      <div className="u-border p-4">
        <div className="d-flex flex-wrap">
          {userImageDiv}
          <div className="ms-auto order-lg-last">
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
          <div>
            <p className="m-0">
              {userProfileUrl ? <a href={userProfileUrl}>{userName}</a> : userName} {getLink(translated.postedComment, commentUrl)}
            </p>
            <p className="m-0">{commentChangeLog}</p>
          </div>
        </div>

        {numReports > 0 &&
          <div>
            <i className="fas fa-exclamation-circle me-1" aria-hidden="true" />
            <strong>{userProfileUrl ? <a href={userProfileUrl}>{userName}</a> : userName}</strong>
            {getLink(translatedReportText(numReports), commentUrl)}
          </div>}

        <p>{commentText}</p>
        <ModerationNotificationActionsBar
          itemPk={notification.pk}
          isEditing={notification.moderator_feedback}
          isBlocked={notification.is_blocked}
          isHighlighted={notification.is_moderator_marked}
          onToggleForm={(isEditing) => toggleModerationFeedbackForm(isEditing)}
          onToggleBlock={() => toggleIsBlocked()}
          onToggleHighlight={() => toggleIsHighlighted()}
        />
        {notification.moderator_feedback && !showFeedbackForm &&
          <ModerationFeedback
            feedback={notification.moderator_feedback}
            onDelete={handleFeedbackDelete}
            onEdit={() => {
              setShowFeedbackForm(true)
              setIsEditing(true)
            }}
          />}
      </div>
      {showFeedbackForm &&
        <ModerationFeedbackForm
          onSubmit={(payload) => handleFeedbackSubmit(payload)}
          onEditSubmit={(payload) => handleFeedbackEdit(payload)}
          initialFeedback={notification.moderator_feedback}
          editing={isEditing}
        />}
      <div className="mb-3">
        <Alert {...alert} onClick={() => setAlert(null)} />
      </div>
    </li>
  )
}
