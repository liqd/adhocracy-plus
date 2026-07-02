// apps/polls/assets/react_polls/components/StartScreen.jsx
import React from 'react'
import django from 'django'
import Alert from 'adhocracy4/adhocracy4/static/Alert'
import { createUnauthenticatedAlert } from '../utils/alerts'

const StartScreen = ({ moduleName, moduleDescription, totalQuestions, isAuthenticated, allowUnregisteredUsers, totalParticipants, onStart, onShowResults }) => {
  return (
    <div className="poll-start-screen">
      {!isAuthenticated && (
        <Alert
          {...createUnauthenticatedAlert(window.adhocracy4.config.getLoginUrl())}
        />
      )}

      {moduleName && <h2>{moduleName}</h2>}

      {moduleDescription && (
        <p className="lead">{moduleDescription}</p>
      )}

      <p
        className="lead"
        dangerouslySetInnerHTML={{
          __html: django.interpolate(
            django.ngettext(
              'Poll contains <span class="poll-start-screen__count">%(count)s question</span>.',
              'Poll contains <span class="poll-start-screen__count">%(count)s questions</span>.',
              totalQuestions
            ),
            { count: totalQuestions },
            true
          ) + ' ' + django.interpolate(
            django.ngettext(
              'So far <span class="poll-start-screen__count">%(count)s person</span> has participated.',
              'So far <span class="poll-start-screen__count">%(count)s people</span> have participated.',
              totalParticipants
            ),
            { count: totalParticipants },
            true
          )
        }}
      />

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
