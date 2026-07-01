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

      <div className="poll poll__preliminary-results-buttons">
        {hasUserVote
          ? (
            <div className="text-end">
              <button
                type="button"
                className="btn btn--transparent"
                onClick={onChangeAnswer}
              >
                {django.gettext('Change my answers')}
              </button>
            </div>
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
