import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { ModerationFeedbackForm } from '../ModerationFeedbackForm'

test('ModerationFeedbackForm without intial value', () => {
  const tree = render(<ModerationFeedbackForm />)
  const textarea = tree.container.querySelector('textarea')
  expect(textarea.value).toBe('')
})

test('ModerationFeedbackForm with initial value', () => {
  const mockProps = { pk: 1, feedback_text: 'test feedback' }
  const tree = render(
    <ModerationFeedbackForm initialFeedback={mockProps} editing />
  )
  const textarea = tree.container.querySelector('textarea')
  expect(textarea.value).toBe(mockProps.feedback_text)
})

test('ModerationFeedbackForm on change value', () => {
  const tree = render(<ModerationFeedbackForm />)
  const textarea = tree.container.querySelector('textarea')
  fireEvent.change(textarea, { target: { value: 'test feedback' } })
  expect(textarea.value).toBe('test feedback')
})

test('ModerationFeedbackForm onSubmit', () => {
  // const mockProps = { pk: 1, feedback: 'test feedback' }
  const callbackFn = jest.fn()
  render(
    <ModerationFeedbackForm
      onSubmit={callbackFn}
    />
  )
  const submitBtn = screen.getByRole('button', { type: 'submit' })
  fireEvent.click(submitBtn)
  expect(callbackFn).toHaveBeenCalled()
})

test('ModerationFeedbackForm onEditSubmit', () => {
  const mockProps = { pk: 1, feedback: 'test feedback' }
  const callbackFn = jest.fn()
  render(
    <ModerationFeedbackForm
      initialFeedback={mockProps}
      editing
      onEditSubmit={callbackFn}
    />
  )
  const submitBtn = screen.getByRole('button', { type: 'submit' })
  fireEvent.click(submitBtn)
  expect(callbackFn).toHaveBeenCalled()
})
