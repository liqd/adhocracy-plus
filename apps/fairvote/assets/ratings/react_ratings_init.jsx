import React from 'react'
import { createRoot } from 'react-dom/client'
import { widget as ReactWidget } from 'adhocracy4'

import RatingChoinsBox from './react_ratings'

export default function init () {
  ReactWidget.initialise('aplus', 'ratings',
    function (el) {
      console.log(el.dataset.attributes)
      const props = JSON.parse(el.dataset.attributes)
      const root = createRoot(el)
      root.render(
        <React.StrictMode>
          <RatingChoinsBox {...props} />
        </React.StrictMode>
      )
    }
  )
}

document.addEventListener('DOMContentLoaded', init, false)
