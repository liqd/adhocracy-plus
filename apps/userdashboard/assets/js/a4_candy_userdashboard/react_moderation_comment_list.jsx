import ModerationCommentList from './ModerationCommentList'
import React from 'react'
import ReactDOM from 'react-dom'

function init () {
  $('[data-aplus-widget="moderation_comment_list"]').each(function (i, element) {
    const moderationCommentList = element.getAttribute('data-moderation-comment-list')
    const projectApiUrl = element.getAttribute('data-project-api-url')
    ReactDOM.render(
      <ModerationCommentList
        moderationCommentList={moderationCommentList}
        projectApiUrl={projectApiUrl}
      />,
      element)
  })
}

document.addEventListener('DOMContentLoaded', init, false)
