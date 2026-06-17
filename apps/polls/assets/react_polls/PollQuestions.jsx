// apps/polls/assets/react_polls/PollQuestions.jsx
import React, { useReducer, useMemo, useEffect } from 'react'
import django from 'django'

import Alert from 'adhocracy4/adhocracy4/static/Alert'
import { TermsOfUseCheckbox } from 'adhocracy4/adhocracy4/static/TermsOfUseCheckbox'
import ProsopoCaptcha from './ProsopoCaptcha'
import StartScreen from './components/StartScreen'
import QuestionFunnel from './components/QuestionFunnel'
import ResultsView from './components/ResultsView'
import { LoadingSpinner } from './components/LoadingSpinner'
import { usePollData } from './hooks/usePollData'
import { usePollActions } from './hooks/usePollActions'
import { pollReducer, initialState } from './reducers/pollReducer'
import { STATES } from './utils/stateMachine'
import { getAnsweredCount } from './utils/pollHelpers'

const PollQuestions = ({ pollId, captchaEnabled, prosopoSiteKey }) => {
  const [state, dispatch] = useReducer(pollReducer, initialState)

  usePollData(pollId, dispatch)

  const actions = usePollActions(state, dispatch, pollId)

  const currentQuestion = useMemo(
    () => state.questions[state.currentQuestionIndex],
    [state.questions, state.currentQuestionIndex]
  )

  const currentAnswer = useMemo(
    () => currentQuestion ? state.userAnswers[currentQuestion.id] : null,
    [currentQuestion, state.userAnswers]
  )

  const answeredCount = useMemo(
    () => getAnsweredCount(state.questions, state.userAnswers),
    [state.questions, state.userAnswers]
  )

  const showCaptcha = state.captchaEnabled &&
    state.allowUnregisteredUsers &&
    !state.isAuthenticated

  useEffect(() => {
    if (state.state === STATES.ANSWERING || state.state === STATES.SUBMITTING) {
      document.body.classList.add('poll-answering')
    } else {
      document.body.classList.remove('poll-answering')
    }
  }, [state.state])

  const renderStateContent = () => {
    switch (state.state) {
      case STATES.LOADING:
        return <LoadingSpinner />

      case STATES.ERROR:
        return (
          <div className="alert alert-danger" role="alert">
            {django.gettext('Failed to load poll data. Please try again.')}
          </div>
        )

      case STATES.RESULTS:
        return (
          <ResultsView
            results={state.results}
            hasUserVote={state.hasUserVote}
            alert={state.alert}
            onBackToPoll={actions.handleBackToPoll}
            onChangeAnswer={actions.handleChangeAnswer}
          />
        )

      case STATES.START_SCREEN:
        return (
          <StartScreen
            totalQuestions={state.questions.length}
            isAuthenticated={state.isAuthenticated}
            allowUnregisteredUsers={state.allowUnregisteredUsers}
            onStart={actions.handleStartPoll}
          />
        )

      case STATES.SUBMITTING:
      case STATES.ANSWERING:
        return (
          <div className="pollquestionlist-container">
            <form onSubmit={(e) => e.preventDefault()}>
              <QuestionFunnel
                currentQuestion={currentQuestion}
                currentAnswer={currentAnswer}
                currentNumber={state.currentQuestionIndex + 1}
                totalQuestions={state.questions.length}
                answeredCount={answeredCount}
                allowUnregisteredUsers={state.allowUnregisteredUsers}
                errors={state.errors}
                onAnswerChange={actions.handleAnswerChange}
                onBack={actions.handleBack}
                onSkip={actions.handleSkip}
                onNext={actions.handleNext}
                onSubmit={actions.handleSubmitAll}
                isLoading={state.isSubmitting}
              />
            </form>

            {state.alert && (
              <Alert onClick={actions.handleClearAlert} {...state.alert} />
            )}

            {state.useTermsOfUse && !state.agreedTermsOfUse && (
              <div className="col-12 mt-4">
                <TermsOfUseCheckbox
                  id="terms-of-use"
                  onChange={actions.handleSetCheckedTerms}
                  orgTermsUrl={state.orgTermsUrl}
                />
              </div>
            )}

            {showCaptcha && (
              <ProsopoCaptcha
                key={state.refreshCaptcha}
                siteKey={prosopoSiteKey}
                language={document.documentElement.lang || 'de'}
                onChange={actions.handleSetCaptcha}
                name="captcha"
              />
            )}
          </div>
        )

      default:
        return null
    }
  }

  return renderStateContent()
}

export default PollQuestions
