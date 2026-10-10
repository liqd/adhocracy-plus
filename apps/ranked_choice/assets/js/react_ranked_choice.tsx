import React from 'react'
import { createRoot } from 'react-dom/client'
import { initialise as ReactWidgetInit } from 'adhocracy4/adhocracy4/static/widget'

import RankedChoiceWidget from './components/RankedChoiceWidget'

function init () {
  ReactWidgetInit('a4', 'ranked_choice',
    function (el: HTMLElement) {
      const props = JSON.parse(el.dataset.attributes || '{}')
      const root = createRoot(el)
      root.render(
        <RankedChoiceWidget {...props} />
      )
    }
  )
}

document.addEventListener('DOMContentLoaded', init, false)