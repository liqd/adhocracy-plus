// apps/polls/assets/react_polls/hooks/usePollSubmission.ts
import { useCallback } from 'react'
import api from 'adhocracy4/adhocracy4/static/api'
import type { PollResultsPayload, UserAnswer } from '../types'

interface SubmitVotesOptions {
  agreedTermsOfUse?: boolean
  captcha?: string
}

export const usePollSubmission = (pollId: number) => {
  const submitVotes = useCallback(async (votes: Record<number, UserAnswer>, options: SubmitVotesOptions = {}) => {
    const { agreedTermsOfUse = false, captcha = '' } = options

    const data: Record<string, unknown> = {
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
        totalParticipants: poll.total_participants || 0,
        votingEnded: poll.voting_ended || false,
        hideResultsUntilFinished: poll.hide_results_until_finished || false
      } as PollResultsPayload & { success: boolean; alert?: unknown; error?: unknown }
    } catch (error) {
      return { success: false, error }
    }
  }, [pollId])

  return { submitVotes }
}
