// apps/polls/assets/react_polls/components/StartScreen.jsx
import React from 'react'
import django from 'django'
import Alert from 'adhocracy4/adhocracy4/static/Alert'
import { createUnauthenticatedAlert } from '../utils/alerts'

const StartScreen = ({ totalQuestions, isAuthenticated, allowUnregisteredUsers, totalParticipants, onStart, onShowResults }) => {
  return (
    <div className="poll-start-screen text-center">
      {!isAuthenticated && (
        <Alert
          {...createUnauthenticatedAlert(window.adhocracy4.config.getLoginUrl())}
        />
      )}

      <h2>{django.gettext('Poll')}</h2>

      <p className="lead">
        {django.interpolate(
          django.ngettext(
            'This poll has %(count)s question.',
            'This poll has %(count)s questions.',
            totalQuestions
          ),
          { count: totalQuestions },
          true
        )}
      </p>

      <div className="poll-start-screen__buttons">
        <button
          type="button"
          className="btn poll__btn--dark"
          onClick={onStart}
          disabled={!isAuthenticated && !allowUnregisteredUsers}
        >
          {django.gettext('Start Poll')}
        </button>

        <button
          type="button"
          className="btn btn--transparent"
          onClick={onShowResults}
        >
          {django.gettext('Show results')}
        </button>
      </div>
    </div>
  )
}

export default StartScreen
