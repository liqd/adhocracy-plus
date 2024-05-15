import React from 'react'
import { createRoot } from 'react-dom/client'
import { widget as ReactWidget } from 'adhocracy4'

import ChoinsBox from './ChoinsBox'

export default function init () {
  ReactWidget.initialise('aplus', 'choins',
    function (el) {
      console.log(el.dataset.attributes)
      const props = JSON.parse(el.dataset.attributes)
      const root = createRoot(el)
      root.render(
        <React.StrictMode>
          <ChoinsBox {...props} />
        </React.StrictMode>
      )
    }
  )
}

document.addEventListener('DOMContentLoaded', init, false)
