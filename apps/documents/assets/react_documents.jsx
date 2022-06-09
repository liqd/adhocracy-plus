import React from 'react'
import { createRoot } from 'react-dom/client'
import DocumentManagement from './DocumentManagement'

module.exports.renderDocumentManagement = function (element) {
  const chapters = JSON.parse(element.getAttribute('data-chapters'))
  const module = element.getAttribute('data-module')
  const config = JSON.parse(element.getAttribute('data-config'))

  const reloadOnSuccess = JSON.parse(element.getAttribute('data-reloadOnSuccess'))

  const root = createRoot(element)
  root.render(<DocumentManagement key={module} module={module} chapters={chapters} config={config} reloadOnSuccess={reloadOnSuccess} />)
}
