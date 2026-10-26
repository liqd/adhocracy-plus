// apps/polls/assets/react_polls/hooks/usePollActions.ts
import { useCallback, type Dispatch } from 'react'
import { ACTIONS } from '../utils/stateMachine'
import { hasValidAnswer, buildVoteData, getUnansweredMandatoryQuestions } from '../utils/pollHelpers'
import { ALERT_INVALID, ALERT_SUCCESS, ALERT_ERROR, ALERT_INCOMPLETE, ALERT_CAPTCHA_INCOMPLETE, MANDATORY_QUESTION_ERROR } from '../utils/alerts'
import { usePollSubmission } from './usePollSubmission'
import type { PollAction, PollQuestion, PollState, UserAnswer } from '../types'

export const usePollActions = (state: PollState, dispatch: Dispatch<PollAction>, pollId: number) => {
  const { submitVotes } = usePollSubmission(pollId)

  const handleStartPoll = useCallback(() => {
    dispatch({ type: ACTIONS.START_POLL })
  }, [dispatch])

  const handleBackToPoll = useCallback(() => {
    dispatch({ type: ACTIONS.BACK_TO_POLL })
  }, [dispatch])

  const handleChangeAnswer = useCallback(() => {
    dispatch({ type: ACTIONS.CHANGE_ANSWER })
  }, [dispatch])

  const showMandatoryErrors = useCallback((questions: PollQuestion[]) => {
    dispatch({
      type: ACTIONS.SET_QUESTION_ERRORS,
      payload: {
        questionIds: questions.map(question => question.id),
        message: MANDATORY_QUESTION_ERROR
      }
    })
  }, [dispatch])

  const handleNext = useCallback(() => {
    const question = state.questions[state.currentQuestionIndex]
    const answer = question ? state.userAnswers[question.id] : undefined

    if (question?.is_mandatory && !hasValidAnswer(question, answer)) {
      showMandatoryErrors([question])
      return
    }

    if (!hasValidAnswer(question, answer)) {
      dispatch({ type: ACTIONS.SET_ALERT, payload: ALERT_INVALID })
      return
    }

    dispatch({ type: ACTIONS.NEXT_QUESTION })
  }, [state.questions, state.currentQuestionIndex, state.userAnswers, dispatch, showMandatoryErrors])

  const handleBack = useCallback(() => {
    dispatch({ type: ACTIONS.PREV_QUESTION })
  }, [dispatch])

  const handleSkip = useCallback(() => {
    const question = state.questions[state.currentQuestionIndex]

    // mandatory questions have no skip: the participant has to answer them
    if (question?.is_mandatory) {
      showMandatoryErrors([question])
      return
    }

    dispatch({ type: ACTIONS.SKIP_QUESTION })
  }, [state.questions, state.currentQuestionIndex, dispatch, showMandatoryErrors])

  const handleShowResults = useCallback(() => {
    dispatch({ type: ACTIONS.SHOW_RESULTS })
  }, [dispatch])

  const handleSubmitAll = useCallback(async () => {
    const showCaptcha = state.captchaEnabled && state.allowUnregisteredUsers && !state.isAuthenticated
    if (showCaptcha && !state.captcha) {
      dispatch({ type: ACTIONS.SET_ALERT, payload: ALERT_CAPTCHA_INCOMPLETE })
      return
    }

    const unanswered = getUnansweredMandatoryQuestions(state.questions, state.userAnswers)
    if (unanswered.length > 0) {
      showMandatoryErrors(unanswered)
      const firstUnansweredIndex = state.questions.findIndex(question => question.id === unanswered[0].id)
      if (firstUnansweredIndex >= 0) {
        dispatch({ type: ACTIONS.GO_TO_QUESTION, payload: firstUnansweredIndex })
      }
      return
    }

    const allValid = state.questions.every(q => {
      const answer = state.userAnswers[q.id]
      return !answer || hasValidAnswer(q, answer)
    })
    if (!allValid) {
      dispatch({ type: ACTIONS.SET_ALERT, payload: ALERT_INCOMPLETE })
      return
    }

    dispatch({ type: ACTIONS.SUBMIT_START })

    const voteData = buildVoteData(state.userAnswers)
    const shouldAgreeTerms = state.useTermsOfUse && !state.agreedTermsOfUse && state.checkedTermsOfUse

    const result = await submitVotes(voteData, {
      agreedTermsOfUse: shouldAgreeTerms,
      captcha: state.captcha
    })

    if (result.success) {
      const resultsHidden = (result as any).hideResultsUntilFinished && !(result as any).votingEnded
      dispatch({
        type: ACTIONS.SUBMIT_SUCCESS,
        payload: {
          ...result,
          alert: resultsHidden ? null : ALERT_SUCCESS
        }
      })
    } else {
      dispatch({ type: ACTIONS.SUBMIT_ERROR, payload: ALERT_ERROR })
    }
  }, [state, dispatch, submitVotes, showMandatoryErrors])

  const handleAnswerChange = useCallback((questionId: number, answerData: UserAnswer) => {
    dispatch({
      type: ACTIONS.UPDATE_ANSWER,
      payload: { questionId, answerData }
    })
  }, [dispatch])

  const handleClearAlert = useCallback(() => {
    dispatch({ type: ACTIONS.CLEAR_ALERT })
  }, [dispatch])

  const handleSetCheckedTerms = useCallback((checked: boolean) => {
    dispatch({ type: ACTIONS.SET_CHECKED_TERMS, payload: checked })
  }, [dispatch])

  const handleSetCaptcha = useCallback((token: string) => {
    dispatch({ type: ACTIONS.SET_CAPTCHA, payload: token })
  }, [dispatch])

  return {
    handleStartPoll,
    handleBackToPoll,
    handleChangeAnswer,
    handleNext,
    handleBack,
    handleSkip,
    handleShowResults,
    handleSubmitAll,
    handleAnswerChange,
    handleClearAlert,
    handleSetCheckedTerms,
    handleSetCaptcha
  }
}
