// apps/polls/assets/react_polls/components/QuestionFunnel.jsx
import React, { useEffect, useRef } from 'react'
import django from 'django'
import { TermsOfUseCheckbox } from 'adhocracy4/adhocracy4/static/TermsOfUseCheckbox'
import { PollChoice } from './PollChoice'
import { PollOpenQuestion } from 'adhocracy4/adhocracy4/polls/static/PollDetail/PollOpenQuestion'
import ProgressBar from './ProgressBar'
import NavigationButtons from './NavigationButtons'

const ANSWER_HANDLERS = {
  single: (questionId, value) => ({ choices: [value] }),
  multi: (questionId, value, currentChoices = []) => ({
    choices: currentChoices.includes(value)
      ? currentChoices.filter(c => c !== value)
      : [...currentChoices, value]
  }),
  open: (questionId, value) => ({ open_answer: value }),
  other: (questionId, value) => ({ other_choice_answer: value })
}

const QuestionFunnel = ({
  currentQuestion,
  currentAnswer,
  currentNumber,
  totalQuestions,
  answeredCount,
  allowUnregisteredUsers,
  useTermsOfUse,
  agreedTermsOfUse,
  orgTermsUrl,
  checkedTermsOfUse,
  onSetCheckedTerms,
  errors,
  onAnswerChange,
  onBack,
  onSkip,
  onNext,
  onSubmit,
  isLoading
}) => {
  const funnelRef = useRef(null)

  useEffect(() => {
    const top = funnelRef.current?.getBoundingClientRect().top + window.scrollY - 50
    window.scrollTo({ top, behavior: 'smooth' })
  }, [currentQuestion.id])

  const isLastQuestion = currentNumber === totalQuestions

  const enrichedQuestion = {
    ...currentQuestion,
    userChoices: currentAnswer?.choices || [],
    open_answer: currentAnswer?.open_answer || '',
    other_choice_answer: currentAnswer?.other_choice_answer || ''
  }

  const handleAnswerUpdate = (questionId, value, type) => {
    const handler = ANSWER_HANDLERS[type]
    if (!handler) return

    const currentChoices = currentAnswer?.choices || []
    const answerData = handler(questionId, value, currentChoices)
    onAnswerChange(questionId, answerData)
  }

  return (
    <div className="poll-question-funnel" ref={funnelRef}>
      <ProgressBar current={currentNumber} total={totalQuestions} />

      <div className="poll-question-header">
        {django.interpolate(
          django.gettext('Question %(current)s of %(total)s'),
          { current: currentNumber, total: totalQuestions },
          true
        )}
      </div>

      <div className="poll-question-content">
        {currentQuestion.is_open
          ? (
            <PollOpenQuestion
              key={currentQuestion.id}
              allowUnregisteredUsers={allowUnregisteredUsers}
              question={enrichedQuestion}
              onOpenChange={(questionId, value) =>
                handleAnswerUpdate(questionId, value, 'open')}
              errors={errors}
              questionImagesEnabled={!!currentQuestion.image_url}
            />
            )
          : (
            <PollChoice
              key={currentQuestion.id}
              question={enrichedQuestion}
              allowUnregisteredUsers={allowUnregisteredUsers}
              onAnswerChange={handleAnswerUpdate}
              errors={errors}
            />
            )}
      </div>

      {isLastQuestion && useTermsOfUse && !agreedTermsOfUse && (
        <div className="col-12 mt-4">
          <TermsOfUseCheckbox
            id="terms-of-use"
            onChange={onSetCheckedTerms}
            orgTermsUrl={orgTermsUrl}
          />
        </div>
      )}

      <NavigationButtons
        onBack={onBack}
        onSkip={onSkip}
        onNext={onNext}
        onSubmit={onSubmit}
        isLoading={isLoading}
        isLastQuestion={isLastQuestion}
        currentIndex={currentNumber - 1}
      />
    </div>
  )
}

export default QuestionFunnel
