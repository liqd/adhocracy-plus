import React from 'react'
import { createRoot } from 'react-dom/client'
import DocumentManagement from './DocumentManagement'
import { widget as ReactWidget } from 'adhocracy4'

function init () {
  ReactWidget.initialise('mb', 'document-management',
    function (el) {
      const chapters = JSON.parse(el.dataset.chapters)
      const module = el.dataset.module
      const config = JSON.parse(el.dataset.config)
      const reloadOnSuccess = JSON.parse(el.dataset.reloadOnSuccess)
      const root = createRoot(el)

      root.render(
        <React.StrictMode>
          <DocumentManagement
            key={module}
            module={module}
            chapters={chapters}
            config={config}
            reloadOnSuccess={reloadOnSuccess}
          />
        </React.StrictMode>
      )
    }
  )
}

document.addEventListener('DOMContentLoaded', init, false)
