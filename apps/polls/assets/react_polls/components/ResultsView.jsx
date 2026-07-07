import React, { useState } from 'react'
import django from 'django'
import PollResults from './PollResults'
import Alert from 'adhocracy4/adhocracy4/static/Alert'

const ResultsView = ({ results, totalParticipants, hasUserVote, alert, onBackToPoll, onChangeAnswer }) => {
  const [resultsCollapsed, setResultsCollapsed] = useState(false)

  return (
    <div className="poll__preliminary-results">
      <button
        type="button"
        className="poll__results-header"
        onClick={() => setResultsCollapsed(!resultsCollapsed)}
        aria-expanded={!resultsCollapsed}
      >
        <div className="poll__results-header-text">
          {totalParticipants > 0 && (
            <p className="poll__total-participants">
              {django.interpolate(
                django.ngettext(
                  '%s person has participated.',
                  '%s people have participated.',
                  totalParticipants
                ),
                [totalParticipants]
              )}
            </p>
          )}
          <p className="lead">{django.gettext('The poll was completed! Here you can see the results.')}</p>
        </div>
        <i className={`fas fa-chevron-down${resultsCollapsed ? '' : ' open'}`} aria-hidden="true" />
      </button>

      <div className={`poll__results-content${resultsCollapsed ? ' poll__results-content--collapsed' : ''}`}>
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
    </div>
  )
}

export default ResultsView
