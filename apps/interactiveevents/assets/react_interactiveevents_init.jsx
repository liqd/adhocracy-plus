import React from 'react'
import { createRoot } from 'react-dom/client'

import QuestionBox from './QuestionBox'
import PresentBox from './PresentBox'
import StatisticsBox from './StatisticsBox'

export function renderLiveQuestions (el) {
  const props = JSON.parse(el.getAttribute('data-attributes'))
  const root = createRoot(el)
  root.render(
    <React.StrictMode>
      <QuestionBox {...props} />
    </React.StrictMode>
  )
}

export function renderLiveQuestionsPresent (el) {
  const props = JSON.parse(el.getAttribute('data-attributes'))
  const root = createRoot(el)
  root.render(
    <React.StrictMode>
      <PresentBox {...props} />
    </React.StrictMode>
  )
}

export function renderLiveQuestionsStatistics (el) {
  const props = JSON.parse(el.getAttribute('data-attributes'))
  const root = createRoot(el)
  root.render(
    <React.StrictMode>
      <StatisticsBox {...props} />
    </React.StrictMode>
  )
}
