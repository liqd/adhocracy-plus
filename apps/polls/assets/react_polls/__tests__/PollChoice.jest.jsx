import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'

import { PollChoice } from '../components/PollChoice'

describe('PollChoice', () => {
  const singleQuestion = {
    id: 1,
    label: 'Pick one',
    multiple_choice: false,
    is_open: false,
    is_confidential: false,
    authenticated: true,
    choices: [
      { id: 10, label: 'Red', is_other_choice: false },
      { id: 11, label: 'Blue', is_other_choice: false }
    ],
    userChoices: []
  }

  const multiQuestion = {
    ...singleQuestion,
    label: 'Pick many',
    multiple_choice: true,
    choices: [
      { id: 10, label: 'Red', is_other_choice: false },
      { id: 11, label: 'Blue', is_other_choice: false },
      { id: 12, label: 'other', is_other_choice: true }
    ]
  }

  it('renders question label', () => {
    render(<PollChoice question={singleQuestion} allowUnregisteredUsers={false} onAnswerChange={jest.fn()} />)
    expect(screen.getByText('Pick one')).toBeInTheDocument()
  })

  it('renders radio inputs for single choice', () => {
    const { container } = render(<PollChoice question={singleQuestion} allowUnregisteredUsers={false} onAnswerChange={jest.fn()} />)
    expect(container.querySelectorAll('input[type="radio"]')).toHaveLength(2)
  })

  it('renders checkbox inputs for multiple choice', () => {
    const { container } = render(<PollChoice question={multiQuestion} allowUnregisteredUsers={false} onAnswerChange={jest.fn()} />)
    expect(container.querySelectorAll('input[type="checkbox"]')).toHaveLength(3)
  })

  it('calls onAnswerChange with single type on radio click', () => {
    const fn = jest.fn()
    render(<PollChoice question={singleQuestion} allowUnregisteredUsers={false} onAnswerChange={fn} />)
    fireEvent.click(screen.getByText('Red'))
    expect(fn).toHaveBeenCalledWith(1, 10, 'single')
  })

  it('calls onAnswerChange with multi type on checkbox click', () => {
    const fn = jest.fn()
    render(<PollChoice question={multiQuestion} allowUnregisteredUsers={false} onAnswerChange={fn} />)
    fireEvent.click(screen.getByText('Red'))
    expect(fn).toHaveBeenCalledWith(1, 10, 'multi')
  })

  it('shows textarea on other selection', () => {
    render(<PollChoice question={multiQuestion} allowUnregisteredUsers={false} onAnswerChange={jest.fn()} />)
    fireEvent.click(screen.getByText('other'))
    expect(screen.getByTestId('textarea-with-counter')).toBeInTheDocument()
  })

  it('shows multiple choice help text', () => {
    render(<PollChoice question={multiQuestion} allowUnregisteredUsers={false} onAnswerChange={jest.fn()} />)
    expect(screen.getByText('Multiple answers are possible.')).toBeInTheDocument()
  })
})
