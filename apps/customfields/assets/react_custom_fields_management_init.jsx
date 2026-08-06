import React from 'react'
import { createRoot } from 'react-dom/client'
import { widget as ReactWidget } from 'adhocracy4'

import { EditCustomFieldManagement } from './CustomFieldManagement/EditCustomFieldManagement'

function init () {
  ReactWidget.initialise('aplus', 'custom-field-management', (el) => {
    const props = JSON.parse(el.dataset.attributes)
    const root = createRoot(el)
    root.render(
      <React.StrictMode>
        <EditCustomFieldManagement {...props} />
      </React.StrictMode>
    )
  })
}

document.addEventListener('DOMContentLoaded', init, false)
