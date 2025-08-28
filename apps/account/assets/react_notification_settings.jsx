import React from 'react'
import { createRoot } from 'react-dom/client'
import NotificationSettings from './NotificationSettings'

function init () {
  const el = document.getElementById('notification-settings-react')
  const root = createRoot(el)
  const notifications = JSON.parse(el.getAttribute('data-initial-notifications'))
  const showRestricted = JSON.parse(el.getAttribute('data-show-restricted'))
  const apiUrl = el.getAttribute('data-api-url')
  root.render(
    <React.StrictMode>
      <NotificationSettings initialNotifications={notifications} showRestricted={showRestricted} apiUrl={apiUrl} />
    </React.StrictMode>)
}

document.addEventListener('DOMContentLoaded', init, false)
document.addEventListener('a4.embed.ready', init, false)
