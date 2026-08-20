import React from 'react'
import { createRoot } from 'react-dom/client'
import { widget as ReactWidget } from 'adhocracy4'

import QuestionBox from './QuestionBox'

function init () {
  ReactWidget.initialise('aplus', 'questions',
    function (el: HTMLElement) {
      const props = JSON.parse(el.dataset.attributes || '{}')
      const root = createRoot(el)
      root.render(
        <React.StrictMode>
          <QuestionBox {...props} />
        </React.StrictMode>
      )
    }
  )
}

document.addEventListener('DOMContentLoaded', init, false)
