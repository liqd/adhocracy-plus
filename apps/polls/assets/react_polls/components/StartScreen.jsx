// apps/polls/assets/react_polls/components/StartScreen.jsx
import React from 'react'
import django from 'django'

const StartScreen = ({ moduleName, moduleDescription, totalQuestions, isAuthenticated, allowUnregisteredUsers, totalParticipants, manualLink, onStart, onShowResults }) => {
  return (
    <div className="poll-start-screen">

      {!isAuthenticated && allowUnregisteredUsers && (
        <aside className="info-box" aria-labelledby="info-box-title">
          <h3 className="visually-hidden" id="info-box-title">{django.gettext('Poll Participation Info')}</h3>
          <div className="info-box__content">
            <i className="far fa-lightbulb" aria-hidden="true" />
            <div className="info-box__text">
              <p>{django.gettext('You can now participate in this poll even if you\'re not logged in.')}</p>
              <p><strong>{django.gettext("Unregistered users can't edit their votes once submitted.")}</strong></p>
              {manualLink && (
                <a href={manualLink + 'pollmodule'} rel="nofollow noopener noreferrer external" target="_blank" className="info-box__link" aria-label={django.gettext('Learn more about the voting options and rules')}>{django.gettext('Learn more about voting options.')}</a>
              )}
            </div>
          </div>
        </aside>
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
        {isAuthenticated || allowUnregisteredUsers
          ? (
            <button
              type="button"
              className="btn poll__btn--dark"
              onClick={onStart}
            >
              {django.gettext('Start')}
            </button>
            )
          : (
            <a
              href={window.adhocracy4?.config?.getLoginUrl?.() || '/accounts/login/'}
              className="btn poll__btn--dark"
            >
              {django.gettext('Log in to participate')}
            </a>
            )}

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
