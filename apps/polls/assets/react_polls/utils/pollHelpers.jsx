export const hasValidAnswer = (question, answer) => {
  if (!answer) return false

  if (question.is_open) {
    return answer.open_answer && answer.open_answer.trim() !== ''
  } else {
    const hasChoice = answer.choices && answer.choices.length > 0
    const hasOtherAnswer = answer.other_choice_answer && answer.other_choice_answer.trim() !== ''
    return hasChoice || hasOtherAnswer
  }
}

export const buildVoteData = (userAnswers) => {
  const voteData = {}
  for (const [questionId, answer] of Object.entries(userAnswers)) {
    voteData[questionId] = {
      choices: answer.choices || [],
      other_choice_answer: answer.other_choice_answer || '',
      open_answer: answer.open_answer || ''
    }
  }
  return voteData
}

export const getAnsweredCount = (questions, userAnswers) => {
  let count = 0
  questions.forEach(question => {
    const answer = userAnswers[question.id]
    if (answer && hasValidAnswer(question, answer)) {
      count++
    }
  })
  return count
}
