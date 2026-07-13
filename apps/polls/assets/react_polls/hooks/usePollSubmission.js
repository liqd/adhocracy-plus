// apps/polls/assets/react_polls/hooks/usePollSubmission.js
import { useCallback } from 'react'
import api from 'adhocracy4/adhocracy4/static/api'

export const usePollSubmission = (pollId, dispatch) => {
  const submitVotes = useCallback(async (votes, options = {}) => {
    const { agreedTermsOfUse = false, captcha = '' } = options

    const data = {
      urlReplaces: { pollId },
      votes,
      captcha
    }

    if (agreedTermsOfUse) {
      data.agreed_terms_of_use = true
    }

    try {
      const poll = await api.poll.vote(data)
      return {
        success: true,
        results: JSON.parse(JSON.stringify(poll.questions)),
        questions: poll.questions,
        useTermsOfUse: poll.use_org_terms_of_use,
        agreedTermsOfUse: poll.user_has_agreed,
        orgTermsUrl: poll.org_terms_url,
        hasUserVote: poll.has_user_vote,
        totalParticipants: poll.total_participants || 0
      }
    } catch (error) {
      return { success: false, error }
    }
  }, [pollId])

  return { submitVotes }
}
