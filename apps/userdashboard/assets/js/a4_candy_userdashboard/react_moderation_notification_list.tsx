import ModerationNotificationList from './ModerationNotificationList'
import React from 'react'
import { createRoot } from 'react-dom/client'
import { widget as ReactWidget } from 'adhocracy4'

function init () {
  ReactWidget.initialise('aplus', 'moderation_notification_list',
    function (el: HTMLElement) {
      const props = el.dataset as any
      const root = createRoot(el)
      root.render(
        <React.StrictMode>
          <ModerationNotificationList {...props} />
        </React.StrictMode>
      )
    }
  )
}

document.addEventListener('DOMContentLoaded', init, false)
