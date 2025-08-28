import React from 'react'
import { createRoot } from 'react-dom/client'
import Notifications from './Notifications'

function init () {
  const el = document.getElementById('notifications-react')
  const root = createRoot(el)
  const notificationsApiUrl = el.getAttribute('data-notifications-api-url')
  const interactionsApiUrl = el.getAttribute('data-interactions-api-url')
  const searchProfilesApiUrl = el.getAttribute('data-search-profiles-api-url')
  const followedProjectsApiUrl = el.getAttribute('data-followed-projects-api-url')
  const planListUrl = el.getAttribute('data-plan-list-url')
  root.render(
    <React.StrictMode>
      <Notifications
        notificationsApiUrl={notificationsApiUrl}
        interactionsApiUrl={interactionsApiUrl}
        searchProfilesApiUrl={searchProfilesApiUrl}
        followedProjectsApiUrl={followedProjectsApiUrl}
        planListUrl={planListUrl}
      />
    </React.StrictMode>)
}

document.addEventListener('DOMContentLoaded', init, false)
document.addEventListener('a4.embed.ready', init, false)
