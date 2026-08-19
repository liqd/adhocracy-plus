import type { PollQuestion, UserAnswer, UserAnswers } from '../types'

export const hasValidAnswer = (question: PollQuestion | undefined, answer: UserAnswer | undefined): boolean => {
  if (!answer) return false

  if (question?.is_open) {
    return !!answer.open_answer && answer.open_answer.trim() !== ''
  }

  const hasChoice = !!answer.choices && answer.choices.length > 0
  const hasOtherAnswer = !!answer.other_choice_answer && answer.other_choice_answer.trim() !== ''

  if (hasChoice && question?.choices) {
    const otherChoice = question.choices.find(c => c.is_other_choice)
    if (otherChoice && answer.choices!.includes(otherChoice.id)) {
      return hasOtherAnswer
    }
  }

  return hasChoice || hasOtherAnswer
}

export const buildVoteData = (userAnswers: UserAnswers): Record<number, UserAnswer> => {
  const voteData: Record<number, UserAnswer> = {}
  for (const [questionId, answer] of Object.entries(userAnswers)) {
    voteData[Number(questionId)] = {
      choices: answer.choices || [],
      other_choice_answer: answer.other_choice_answer || '',
      open_answer: answer.open_answer || ''
    }
  }
  return voteData
}

export const getAnsweredCount = (questions: PollQuestion[], userAnswers: UserAnswers): number => {
  let count = 0
  questions.forEach(question => {
    const answer = userAnswers[question.id]
    if (answer && hasValidAnswer(question, answer)) {
      count++
    }
  })
  return count
}
