import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'

import QuestionFunnel from '../components/QuestionFunnel'

describe('QuestionFunnel', () => {
  const choiceQuestion = {
    id: 1,
    label: 'Favorite color',
    is_open: false,
    multiple_choice: false,
    is_confidential: false,
    authenticated: true,
    choices: [
      { id: 10, label: 'Red', is_other_choice: false },
      { id: 11, label: 'Blue', is_other_choice: false }
    ]
  }

  const openQuestion = {
    id: 2, label: 'Your thoughts', is_open: true, authenticated: true
  }

  const baseProps = {
    currentQuestion: choiceQuestion,
    currentAnswer: null,
    currentNumber: 1,
    totalQuestions: 3,
    answeredCount: 0,
    allowUnregisteredUsers: false,
    errors: null,
    onAnswerChange: jest.fn(),
    onBack: jest.fn(),
    onSkip: jest.fn(),
    onNext: jest.fn(),
    onSubmit: jest.fn(),
    isLoading: false
  }

  it('renders question header with numbering', () => {
    render(<QuestionFunnel {...baseProps} currentNumber={1} totalQuestions={3} />)
    expect(screen.getByText('Question 1 of 3')).toBeInTheDocument()
  })

  it('renders ProgressBar', () => {
    render(<QuestionFunnel {...baseProps} answeredCount={1} totalQuestions={3} />)
    expect(screen.getByText('1 of 3 questions answered')).toBeInTheDocument()
  })

  it('renders PollChoice for non-open questions', () => {
    render(<QuestionFunnel {...baseProps} />)
    expect(screen.getByText('Favorite color')).toBeInTheDocument()
    expect(screen.getByText('Red')).toBeInTheDocument()
    expect(screen.getByText('Blue')).toBeInTheDocument()
  })

  it('renders PollOpenQuestion for open questions', () => {
    render(<QuestionFunnel {...baseProps} currentQuestion={openQuestion} />)
    expect(screen.getByTestId('poll-open-question')).toBeInTheDocument()
  })

  it('calls onNext on Next click', () => {
    const fn = jest.fn()
    render(<QuestionFunnel {...baseProps} onNext={fn} />)
    fireEvent.click(screen.getByText('Next'))
    expect(fn).toHaveBeenCalledTimes(1)
  })

  it('calls onBack on Back click', () => {
    const fn = jest.fn()
    render(<QuestionFunnel {...baseProps} currentNumber={2} totalQuestions={3} onBack={fn} />)
    fireEvent.click(screen.getByText('Back'))
    expect(fn).toHaveBeenCalledTimes(1)
  })

  it('calls onSkip on Skip click', () => {
    const fn = jest.fn()
    render(<QuestionFunnel {...baseProps} onSkip={fn} />)
    fireEvent.click(screen.getByText('Skip'))
    expect(fn).toHaveBeenCalledTimes(1)
  })

  it('shows Submit All and calls onSubmit on last question', () => {
    const fn = jest.fn()
    render(<QuestionFunnel {...baseProps} currentNumber={3} totalQuestions={3} onSubmit={fn} />)
    expect(screen.getByText('Submit All')).toBeInTheDocument()
    fireEvent.click(screen.getByText('Submit All'))
    expect(fn).toHaveBeenCalledTimes(1)
  })

  it('shows Submitting... when loading on last question', () => {
    render(<QuestionFunnel {...baseProps} currentNumber={3} totalQuestions={3} isLoading />)
    expect(screen.getByText('Submitting...')).toBeDisabled()
  })

  it('enriches question with currentAnswer and forwards answer changes', () => {
    const fn = jest.fn()
    render(
      <QuestionFunnel
        {...baseProps}
        currentAnswer={{ choices: [10], open_answer: '', other_choice_answer: '' }}
        onAnswerChange={fn}
      />
    )
    expect(screen.getByText('Red').closest('label').querySelector('input')).toBeChecked()
    fireEvent.click(screen.getByText('Blue'))
    expect(fn).toHaveBeenCalledWith(1, { choices: [11] })
  })

  it('forwards open question answer changes', () => {
    const fn = jest.fn()
    render(
      <QuestionFunnel
        {...baseProps}
        currentQuestion={{ id: 3, label: 'Your thoughts', is_open: true, authenticated: true }}
        onAnswerChange={fn}
      />
    )
    const container = screen.getByTestId('poll-open-question')
    expect(container).toBeInTheDocument()
  })
})
