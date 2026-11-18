// apps/polls/assets/react_polls/PollQuestions.tsx
import React, { useReducer, useMemo, useEffect } from 'react'
import django from 'django'

import Alert from 'adhocracy4/adhocracy4/static/Alert'
import ProsopoCaptcha from '../ProsopoCaptcha'
import StartScreen from './StartScreen'
import QuestionFunnel from './QuestionFunnel'
import ResultsView from './ResultsView'
import PollAnswerReview from './PollAnswerReview'
import { LoadingSpinner } from './LoadingSpinner'
import { usePollData } from '../hooks/usePollData'
import { usePollActions } from '../hooks/usePollActions'
import { pollReducer, initialState } from '../reducers/pollReducer'
import { STATES } from '../utils/stateMachine'

const captchaWidgets: Record<string, React.FC<any>> = {
  prosopo: ProsopoCaptcha
}

function getCaptchaWidget (type: string | undefined) {
  return captchaWidgets[type || 'prosopo']
}

interface PollQuestionsProps {
  pollId: number
  captchaEnabled?: boolean
  captchaType?: string
  prosopoSiteKey?: string
  manualLink?: string
}

const PollQuestions = ({ pollId, captchaEnabled, captchaType, prosopoSiteKey, manualLink }: PollQuestionsProps) => {
  const [state, dispatch] = useReducer(pollReducer, initialState)

  usePollData(pollId, dispatch)

  const actions = usePollActions(state, dispatch, pollId)
  const CaptchaWidget = getCaptchaWidget(captchaType)

  const currentQuestion = useMemo(
    () => state.questions[state.currentQuestionIndex],
    [state.questions, state.currentQuestionIndex]
  )

  const currentAnswer = useMemo(
    () => currentQuestion ? state.userAnswers[currentQuestion.id] : null,
    [currentQuestion, state.userAnswers]
  )

  const showCaptcha = !!captchaEnabled &&
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
        if (!state.hideResultsUntilFinished || state.votingEnded) {
          return (
            <ResultsView
              results={state.results}
              totalParticipants={state.totalParticipants}
              hasUserVote={state.hasUserVote}
              votingEnded={state.votingEnded}
              alert={state.alert}
              onBackToPoll={actions.handleBackToPoll}
              onChangeAnswer={actions.handleChangeAnswer}
            />
          )
        }

        return (
          <PollAnswerReview
            questions={state.questions}
            onChangeAnswer={actions.handleChangeAnswer}
          />
        )

      case STATES.START_SCREEN:
        return (
          <StartScreen
            totalQuestions={state.questions.length}
            totalParticipants={state.totalParticipants}
            isAuthenticated={state.isAuthenticated}
            allowUnregisteredUsers={state.allowUnregisteredUsers}
            hideResultsUntilFinished={state.hideResultsUntilFinished}
            manualLink={manualLink}
            onStart={actions.handleStartPoll}
            onShowResults={actions.handleShowResults}
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
                allowUnregisteredUsers={state.allowUnregisteredUsers}
                errors={state.errors}
                onAnswerChange={actions.handleAnswerChange}
                onBack={actions.handleBack}
                onSkip={actions.handleSkip}
                onNext={actions.handleNext}
                onSubmit={actions.handleSubmitAll}
                isLoading={state.isSubmitting}
                useTermsOfUse={state.useTermsOfUse}
                agreedTermsOfUse={state.agreedTermsOfUse}
                orgTermsUrl={state.orgTermsUrl}
                checkedTermsOfUse={state.checkedTermsOfUse}
                onSetCheckedTerms={actions.handleSetCheckedTerms}
                showCaptcha={showCaptcha}
                captcha={state.captcha}
              >
                {showCaptcha && (
                  <CaptchaWidget
                    key={state.refreshCaptcha}
                    siteKey={prosopoSiteKey}
                    language={document.documentElement.lang || 'de'}
                    onChange={actions.handleSetCaptcha}
                    name="captcha"
                  />
                )}
              </QuestionFunnel>
            </form>

            {state.alert && (
              <Alert onClick={actions.handleClearAlert} {...state.alert} />
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
