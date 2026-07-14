// apps/polls/assets/react_polls/components/QuestionFunnel.jsx
import React, { useState, useCallback, useLayoutEffect, useRef } from 'react'
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
  showCaptcha,
  captcha,
  onSetCheckedTerms,
  errors,
  onAnswerChange,
  onBack,
  onSkip,
  onNext,
  onSubmit,
  isLoading,
  children
}) => {
  const funnelRef = useRef(null)
  const headerRef = useRef(null)
  const prevNumberRef = useRef(currentNumber)
  const prevQuestionRef = useRef(currentQuestion)
  const prevAnswerRef = useRef(currentAnswer)

  const [phase, setPhase] = useState('idle')
  const [direction, setDirection] = useState('forward')
  const [exitingQuestion, setExitingQuestion] = useState(null)
  const [exitingAnswer, setExitingAnswer] = useState(null)

  useLayoutEffect(() => {
    const top = funnelRef.current?.getBoundingClientRect().top + window.scrollY - 50
    window.scrollTo({ top, behavior: 'smooth' })
    headerRef.current?.focus({ preventScroll: true })
  }, [currentQuestion.id])

  useLayoutEffect(() => {
    if (currentNumber !== prevNumberRef.current) {
      const dir = currentNumber > prevNumberRef.current ? 'forward' : 'backward'
      setDirection(dir)
      setExitingQuestion(prevQuestionRef.current)
      setExitingAnswer(prevAnswerRef.current)
      setPhase('exiting')
      prevNumberRef.current = currentNumber
    }
    prevQuestionRef.current = currentQuestion
    prevAnswerRef.current = currentAnswer
  }, [currentNumber, currentQuestion, currentAnswer])

  const handleExitEnd = useCallback(() => {
    setExitingQuestion(null)
    setExitingAnswer(null)
    setPhase('entering')
  }, [])

  const handleEnterEnd = useCallback(() => {
    setPhase('idle')
  }, [])

  const enrichQuestion = useCallback((question, answer) => ({
    ...question,
    userChoices: answer?.choices || [],
    open_answer: answer?.open_answer || '',
    other_choice_answer: answer?.other_choice_answer || ''
  }), [])

  const isLastQuestion = currentNumber === totalQuestions
  const isSubmitDisabled = (isLastQuestion && useTermsOfUse && !agreedTermsOfUse && !checkedTermsOfUse) ||
    (isLastQuestion && showCaptcha && !captcha)

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

      <div className="poll-question-header" tabIndex={-1} ref={headerRef}>
        {django.interpolate(
          django.gettext('Question %(current)s of %(total)s'),
          { current: currentNumber, total: totalQuestions },
          true
        )}
      </div>

      <div className="poll-question-content-wrapper">
        {phase === 'exiting'
          ? (
            <div
              className={'poll-question-content poll-question-content--exit-' + direction}
              onAnimationEnd={handleExitEnd}
            >
              {exitingQuestion?.is_open
                ? (
                  <PollOpenQuestion
                    key={exitingQuestion.id}
                    allowUnregisteredUsers={allowUnregisteredUsers}
                    question={enrichQuestion(exitingQuestion, exitingAnswer)}
                    onOpenChange={() => {}}
                    errors={errors}
                    questionImagesEnabled={!!exitingQuestion.image_url}
                  />
                  )
                : (
                  <PollChoice
                    key={exitingQuestion?.id}
                    question={enrichQuestion(exitingQuestion, exitingAnswer)}
                    allowUnregisteredUsers={allowUnregisteredUsers}
                    onAnswerChange={() => {}}
                    errors={errors}
                  />
                  )}
            </div>
            )
          : (
            <div
              className={'poll-question-content poll-question-content--enter-' + direction + (phase === 'idle' ? '' : '')}
              onAnimationEnd={phase === 'entering' ? handleEnterEnd : undefined}
            >
              {currentQuestion.is_open
                ? (
                  <PollOpenQuestion
                    key={currentQuestion.id}
                    allowUnregisteredUsers={allowUnregisteredUsers}
                    question={enrichQuestion(currentQuestion, currentAnswer)}
                    onOpenChange={(questionId, value) =>
                      handleAnswerUpdate(questionId, value, 'open')}
                    errors={errors}
                    questionImagesEnabled={!!currentQuestion.image_url}
                  />
                  )
                : (
                  <PollChoice
                    key={currentQuestion.id}
                    question={enrichQuestion(currentQuestion, currentAnswer)}
                    allowUnregisteredUsers={allowUnregisteredUsers}
                    onAnswerChange={handleAnswerUpdate}
                    errors={errors}
                  />
                  )}
            </div>
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

      {isLastQuestion && children}

      <NavigationButtons
        onBack={onBack}
        onSkip={onSkip}
        onNext={onNext}
        onSubmit={onSubmit}
        isLoading={isLoading}
        isLastQuestion={isLastQuestion}
        isSubmitDisabled={isSubmitDisabled}
        currentIndex={currentNumber - 1}
      />
    </div>
  )
}

export default QuestionFunnel
