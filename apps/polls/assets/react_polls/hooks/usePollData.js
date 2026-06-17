// apps/polls/assets/react_polls/hooks/usePollData.js
import { useEffect } from 'react'
import api from 'adhocracy4/adhocracy4/static/api'
import django from 'django'

const normalizePollData = (poll) => {
  const userAnswers = {}

  poll.questions.forEach(question => {
    const hasUserChoices = question.userChoices?.length > 0

    // Open question: API provides answers[] + userAnswer (Answer ID), not a flat open_answer field
    const existingOpenAnswer = question.is_open && question.userAnswer
      ? question.answers?.find(a => a.id === question.userAnswer)?.answer || ''
      : (question.open_answer || '')

    const hasOpenAnswer = existingOpenAnswer !== ''

    // Choice question with "other": API provides other_choice_answers[] + other_choice_user_answer (Vote ID)
    const existingOtherAnswer = !question.is_open && question.other_choice_user_answer
      ? question.other_choice_answers?.find(a => a.vote_id === question.other_choice_user_answer)?.answer || ''
      : (question.other_choice_answer || '')

    if (hasUserChoices || hasOpenAnswer) {
      userAnswers[question.id] = {
        choices: question.userChoices || [],
        open_answer: existingOpenAnswer,
        other_choice_answer: existingOtherAnswer
      }
    }
  })

  const isAuthenticated = poll.questions.length > 0 &&
    poll.questions[0]?.authenticated

  return {
    questions: poll.questions,
    userAnswers,
    results: JSON.parse(JSON.stringify(poll.questions)),
    allowUnregisteredUsers: poll.allow_unregistered_users,
    isAuthenticated,
    hasUserVote: poll.has_user_vote,
    useTermsOfUse: poll.use_org_terms_of_use,
    agreedTermsOfUse: poll.user_has_agreed,
    orgTermsUrl: poll.org_terms_url
  }
}

export const usePollData = (pollId, dispatch) => {
  useEffect(() => {
    if (!pollId) return

    api.poll.get(pollId)
      .done((poll) => {
        dispatch({
          type: 'DATA_LOADED',
          payload: normalizePollData(poll)
        })
      })
      .fail((error) => {
        console.log(error)
        dispatch({
          type: 'DATA_ERROR',
          payload: {
            type: 'danger',
            message: django.gettext('Failed to load poll data. Please try again.')
          }
        })
      })
  }, [pollId, dispatch])
}
