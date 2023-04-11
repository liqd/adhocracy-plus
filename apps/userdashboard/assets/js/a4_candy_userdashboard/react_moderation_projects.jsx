import ModerationProjects from './ModerationProjects'
import React from 'react'
import { createRoot } from 'react-dom/client'
import { widget as ReactWidget } from 'adhocracy4'

function init () {
  ReactWidget.initialise('aplus', 'moderation_projects',
    function (el) {
      const projectApiUrl = el.dataset.projectApiUrl
      const root = createRoot(el)
      root.render(
        <ModerationProjects
          projectApiUrl={projectApiUrl}
        />
      )
    })
}

document.addEventListener('DOMContentLoaded', init, false)
