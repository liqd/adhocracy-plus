import React from 'react'
import { createRoot } from 'react-dom/client'
import { widget as ReactWidget } from 'adhocracy4'

import ModuleList from './ModuleList'

export default function init () {
  ReactWidget.initialise('aplus', 'fv_modules',
    function (el) {
      console.log(el.dataset.attributes)
      const props = JSON.parse(el.dataset.attributes)
      const root = createRoot(el)
      root.render(
        <React.StrictMode>
          <ModuleList {...props} />
        </React.StrictMode>
      )
    }
  )
}

document.addEventListener('DOMContentLoaded', init, false)
