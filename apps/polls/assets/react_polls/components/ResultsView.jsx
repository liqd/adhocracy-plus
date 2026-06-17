// apps/polls/assets/react_polls/components/ResultsView.jsx
import React from 'react'
import django from 'django'
import PollResults from './PollResults'
import Alert from 'adhocracy4/adhocracy4/static/Alert'

const ResultsView = ({ results, hasUserVote, alert, onBackToPoll, onChangeAnswer }) => {
  return (
    <div className="poll__preliminary-results">
      {results.map((question, idx) => (
        <PollResults key={`result-${question.id || idx}`} question={question} />
      ))}

      {alert && <Alert {...alert} />}

      <div className="poll">
        {hasUserVote
          ? (
            <button
              type="button"
              className="btn poll__btn--link"
              onClick={onChangeAnswer}
            >
              {django.gettext('Change answer')}
            </button>
            )
          : (
            <button
              type="button"
              className="btn poll__btn--link"
              onClick={onBackToPoll}
            >
              {django.gettext('To poll')}
            </button>
            )}
      </div>
    </div>
  )
}

export default ResultsView
