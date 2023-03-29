import React, { useState } from 'react'
import django from 'django'
import api from './api'
import { ModerationStatementForm } from './ModerationStatementForm'
import { ModerationStatement } from './ModerationStatement'
import { ModerationNotificationActionsBar } from './ModerationNotificationActionsBar'
import { alert as Alert } from 'adhocracy4'

const alertTime = 6000

const translated = {
  statementAdded: django.pgettext('kosmo', 'Your feedback was successfully delivered.'),
  statementEdited: django.pgettext('kosmo', 'Your feedback was successfully updated.'),
  statementDeleted: django.pgettext('kosmo', 'Your feedback was successfully deleted.'),
  anotherStatement: django.pgettext('kosmo', 'The comment has already been moderated. Your feedback could not be saved.'),
  goToDiscussion: django.pgettext('kosmo', 'Go to discussion'),
  commentBlocked: django.pgettext('kosmo', 'Comment blocked successfully.'),
  commentUnblocked: django.pgettext('kosmo', 'Comment unblocked successfully.'),
  commentHighlighted: django.pgettext('kosmo', 'Comment highlighted successfully.'),
  commentUnhighlighted: django.pgettext('kosmo', 'Comment unhighlighted successfully.'),
  notificationRead: django.pgettext('kosmo', 'Notification successfully marked as read.'),
  notificationUnread: django.pgettext('kosmo', 'Notification successfully marked as unread.'),
  aiClassified: django.pgettext('kosmo', 'AI')
}

export const ModerationNotification = (props) => {
  const { notification } = props
  const [showStatementForm, setShowStatementForm] = useState(false)
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
  function getStatementAdded (commentUrl) {
    return (
      <>
        {translated.statementAdded} <a href={commentUrl}>{translated.goToDiscussion}</a>
      </>
    )
  }

  // **** Start statement methods ****

  const handleStatementSubmit = async (payload) => {
    const [getResponse] = await api.fetch({
      url: notification.feedback_api_url,
      method: 'GET'
    })

    if (getResponse.length > 0) {
      setShowStatementForm(false)
      setAlert({
        type: 'error',
        message: translated.anotherStatement,
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
        setShowStatementForm(false)
        setAlert({
          type: 'success',
          message: getStatementAdded(),
          timeInMs: alertTime
        })
      }
    }
  }

  const handleStatementEdit = async (payload) => {
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
      setShowStatementForm(false)
      setIsEditing(false)
      setAlert({
        type: 'success',
        message: translated.statementEdited,
        timeInMs: alertTime
      })
    }
  }

  const handleStatementDelete = async () => {
    await api.fetch({
      url: notification.feedback_api_url + notification.moderator_feedback.pk + '/',
      method: 'DELETE'
    })
    props.loadData()
    setAlert({
      type: 'success',
      message: translated.statementDeleted,
      timeInMs: alertTime
    })
  }

  function toggleModerationStatementForm (isEditing) {
    isEditing && setIsEditing(true)
    setShowStatementForm(!showStatementForm)
  }

  // **** End statement methods ****

  // **** Start notification methods ****

  async function toggleIsPending () {
    const url = notification.is_unread
      ? props.apiUrl + 'mark_read/'
      : props.apiUrl + 'mark_unread/'
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
        url: props.apiUrl,
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
        url: props.apiUrl,
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
    const tmp = django.npgettext(
      'kosmo',
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
  const markReadText = django.pgettext('kosmo, verb', 'Mark as read')

  let userImageDiv
  if (userImage) {
    const sectionStyle = {
      backgroundImage: 'url(' + userImage + ')'
    }
    userImageDiv = <div className="user-avatar user-avatar--small user-avatar--shadow mb-1 userindicator__btn-img" style={sectionStyle} />
  }

  let commentChangeLog
  if (isModified) {
    commentChangeLog = django.pgettext('kosmo', 'Last edited on ' + created)
  } else {
    commentChangeLog = django.pgettext('kosmo', 'Created on ' + created)
  }

  return (
    <>
      <li className="list-item">
        <div className="d-flex flex-wrap">
          {userImageDiv}
          {notification.is_unread &&
            <div className="ms-auto order-lg-last">
              <div className="dropdown">
                <button
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
                      onClick={() => toggleIsPending()}
                    >
                      {markReadText}
                    </button>
                  </li>
                </ul>
              </div>
            </div>}
          <div className="pt-1">{commentChangeLog}</div>
        </div>

        <div>
          <i className="fas fa-exclamation-circle me-1" aria-hidden="true" />
          <strong>{userProfileUrl ? <a href={userProfileUrl}>{userName}</a> : userName}</strong>
          {getLink(translatedReportText(numReports), commentUrl)}
        </div>
        <p>{commentText}</p>
        <ModerationNotificationActionsBar
          isPending={notification.is_unread}
          isEditing={notification.moderator_feedback}
          isBlocked={notification.is_blocked}
          isHighlighted={notification.is_moderator_marked}
          onToggleForm={(isEditing) => toggleModerationStatementForm(isEditing)}
          onToggleBlock={() => toggleIsBlocked()}
          onToggleHighlight={() => toggleIsHighlighted()}
          onTogglePending={() => toggleIsPending()}
        />
        {showStatementForm &&
          <ModerationStatementForm
            onSubmit={(payload) => handleStatementSubmit(payload)}
            onEditSubmit={(payload) => handleStatementEdit(payload)}
            initialStatement={notification.moderator_feedback}
            editing={isEditing}
          />}
        {notification.moderator_feedback && !showStatementForm &&
          <ModerationStatement
            notificationIsPending={notification.is_unread}
            statement={notification.moderator_feedback}
            onDelete={handleStatementDelete}
            onEdit={() => {
              setShowStatementForm(true)
              setIsEditing(true)
            }}
          />}
      </li>
      <div className="mb-3">
        <Alert {...alert} onClick={() => setAlert(null)} />
      </div>
    </>
  )
}
