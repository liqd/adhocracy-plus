import ModerationNotificationList from './ModerationNotificationList'
import React from 'react'
import ReactDOM from 'react-dom'

function init () {
  $('[data-aplus-widget="moderation_notification_list"]').each(function (i, element) {
    const moderationCommentsApiUrl = element.getAttribute('data-moderation-comments-api-url')
    const projectTitle = element.getAttribute('data-project-title')
    const organisation = element.getAttribute('data-organisation')
    const projectUrl = element.getAttribute('data-project-url')
    ReactDOM.render(
      <ModerationNotificationList
        moderationCommentsApiUrl={moderationCommentsApiUrl}
        projectTitle={projectTitle}
        organisation={organisation}
        projectUrl={projectUrl}
      />,
      element)
  })
}

document.addEventListener('DOMContentLoaded', init, false)
