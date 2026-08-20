// apps/polls/assets/react_polls/components/QuestionFunnel.tsx
import React, { useState, useCallback, useLayoutEffect, useRef } from 'react'
import django from 'django'
import { TermsOfUseCheckbox } from 'adhocracy4/adhocracy4/static/TermsOfUseCheckbox'
import { PollChoice } from './PollChoice'
import { PollOpenQuestion } from 'adhocracy4/adhocracy4/polls/static/PollDetail/PollOpenQuestion'
import ProgressBar from './ProgressBar'
import NavigationButtons from './NavigationButtons'
import type { PollQuestion, UserAnswer } from '../types'

const ANSWER_HANDLERS: Record<string, (questionId: number, value: string | number, currentChoices?: number[]) => Partial<UserAnswer>> = {
  single: (questionId, value) => ({ choices: [Number(value)] }),
  multi: (questionId, value, currentChoices = []) => {
    const val = Number(value)
    return {
      choices: currentChoices.includes(val)
        ? currentChoices.filter(c => c !== val)
        : [...currentChoices, val]
    }
  },
  open: (questionId, value) => ({ open_answer: String(value) }),
  other: (questionId, value) => ({ other_choice_answer: String(value) })
}

interface QuestionFunnelProps {
  currentQuestion: PollQuestion
  currentAnswer?: UserAnswer | null
  currentNumber: number
  totalQuestions: number
  allowUnregisteredUsers: boolean
  useTermsOfUse: boolean
  agreedTermsOfUse: boolean
  orgTermsUrl: string
  checkedTermsOfUse: boolean
  showCaptcha: boolean
  captcha: string
  onSetCheckedTerms: (checked: boolean) => void
  errors: Record<string, unknown>
  onAnswerChange: (questionId: number, answerData: Partial<UserAnswer>) => void
  onBack: () => void
  onSkip: () => void
  onNext: () => void
  onSubmit: () => void
  isLoading: boolean
  children?: React.ReactNode
}

const QuestionFunnel = ({
  currentQuestion,
  currentAnswer,
  currentNumber,
  totalQuestions,
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
}: QuestionFunnelProps) => {
  const funnelRef = useRef<HTMLDivElement>(null)
  const headerRef = useRef<HTMLDivElement>(null)
  const prevNumberRef = useRef(currentNumber)
  const prevQuestionRef = useRef<PollQuestion | null>(currentQuestion)
  const prevAnswerRef = useRef<UserAnswer | null | undefined>(currentAnswer)

  const [phase, setPhase] = useState('idle')
  const [direction, setDirection] = useState('forward')
  const [exitingQuestion, setExitingQuestion] = useState<PollQuestion | null>(null)
  const [exitingAnswer, setExitingAnswer] = useState<UserAnswer | null>(null)

  useLayoutEffect(() => {
    const top = (funnelRef.current?.getBoundingClientRect().top || 0) + window.scrollY - 50
    window.scrollTo({ top, behavior: 'smooth' })
    headerRef.current?.focus({ preventScroll: true })
  }, [currentQuestion.id])

  useLayoutEffect(() => {
    if (currentNumber !== prevNumberRef.current) {
      const dir = currentNumber > prevNumberRef.current ? 'forward' : 'backward'
      setDirection(dir)
      setExitingQuestion(prevQuestionRef.current)
      setExitingAnswer(prevAnswerRef.current ?? null)
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

  const enrichQuestion = useCallback((question: PollQuestion, answer: UserAnswer | null | undefined): PollQuestion => ({
    ...question,
    userChoices: answer?.choices || [],
    open_answer: answer?.open_answer || '',
    other_choice_answer: answer?.other_choice_answer || ''
  }), [])

  const isLastQuestion = currentNumber === totalQuestions
  const isSubmitDisabled = (isLastQuestion && useTermsOfUse && !agreedTermsOfUse && !checkedTermsOfUse) ||
    (isLastQuestion && showCaptcha && !captcha)

  const handleAnswerUpdate = (questionId: number, value: string | number, type: string) => {
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
        {phase === 'exiting' && exitingQuestion
          ? (
            <div
              className={'poll-question-content poll-question-content--exit-' + direction}
              onAnimationEnd={handleExitEnd}
            >
              {exitingQuestion.is_open
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
                    key={exitingQuestion.id}
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
                    onOpenChange={(questionId: number, value: string) =>
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
