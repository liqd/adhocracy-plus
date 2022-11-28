import React from 'react'
import { createRoot } from 'react-dom/client'

import QuestionBox from './livequestion_box'
import PresentBox from './livequestion_present_box'
import StatisticsBox from './livequestion_statistics_box'

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
