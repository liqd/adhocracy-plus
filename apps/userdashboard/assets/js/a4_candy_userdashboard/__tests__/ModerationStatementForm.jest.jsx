import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { ModerationStatementForm } from '../ModerationStatementForm'

test('ModerationStatementForm without intial value', () => {
  const tree = render(<ModerationStatementForm />)
  const textarea = tree.container.querySelector('textarea')
  expect(textarea.value).toBe('')
})

test('ModerationStatementForm with initial value', () => {
  const mockProps = { pk: 1, statement: 'test statement' }
  const tree = render(
    <ModerationStatementForm initialStatement={mockProps} editing />
  )
  const textarea = tree.container.querySelector('textarea')
  expect(textarea.value).toBe(mockProps.statement)
})

test('ModerationStatementForm on change value', () => {
  const tree = render(<ModerationStatementForm />)
  const textarea = tree.container.querySelector('textarea')
  fireEvent.change(textarea, { target: { value: 'test statement' } })
  expect(textarea.value).toBe('test statement')
})

test('ModerationStatementForm onSubmit', () => {
  // const mockProps = { pk: 1, statement: 'test statement' }
  const callbackFn = jest.fn()
  render(
    <ModerationStatementForm
      onSubmit={callbackFn}
    />
  )
  const submitBtn = screen.getByRole('button', { type: 'submit' })
  fireEvent.click(submitBtn)
  expect(callbackFn).toHaveBeenCalled()
})

test('ModerationStatementForm onEditSubmit', () => {
  const mockProps = { pk: 1, statement: 'test statement' }
  const callbackFn = jest.fn()
  render(
    <ModerationStatementForm
      initialStatement={mockProps}
      editing
      onEditSubmit={callbackFn}
    />
  )
  const submitBtn = screen.getByRole('button', { type: 'submit' })
  fireEvent.click(submitBtn)
  expect(callbackFn).toHaveBeenCalled()
})
