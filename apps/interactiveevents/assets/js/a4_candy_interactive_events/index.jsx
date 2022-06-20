import React from 'react'
import ReactDOM from 'react-dom'

import QuestionBox from './livequestion_box'
import PresentBox from './livequestion_present_box'
import StatisticsBox from './livequestion_statistics_box'

export function renderLiveQuestions (el) {
  const props = JSON.parse(el.getAttribute('data-attributes'))
  ReactDOM.render(<QuestionBox {...props} />, el)
}

export function renderLiveQuestionsPresent (el) {
  const props = JSON.parse(el.getAttribute('data-attributes'))
  ReactDOM.render(<PresentBox {...props} />, el)
}

export function renderLiveQuestionsStatistics (el) {
  const props = JSON.parse(el.getAttribute('data-attributes'))
  ReactDOM.render(<StatisticsBox {...props} />, el)
}
