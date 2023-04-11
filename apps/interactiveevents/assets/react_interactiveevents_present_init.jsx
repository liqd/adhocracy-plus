import React from 'react'
import { createRoot } from 'react-dom/client'
import { widget as ReactWidget } from 'adhocracy4'

import PresentBox from './PresentBox'

function init () {
  ReactWidget.initialise('aplus', 'present',
    function (el) {
      const props = JSON.parse(el.dataset.attributes)
      const root = createRoot(el)
      root.render(
        <React.StrictMode>
          <PresentBox {...props} />
        </React.StrictMode>
      )
    }
  )
}

document.addEventListener('DOMContentLoaded', init, false)
