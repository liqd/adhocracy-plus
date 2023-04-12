import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { ModerationFeedback } from '../ModerationFeedback'

test('ModerationFeedback with optimal values', () => {
  const mockProps = {
    feedback_text: 'test feedback',
    last_edit: '20. April 2022, 3 PM',
    pk: 1
  }
  render(
    <ModerationFeedback feedback={mockProps} />
  )
  const feedback = screen.getByText('test feedback')
  expect(feedback).toBeTruthy()
})

test('ModerationFeedback onDelete', () => {
  const mockProps = {
    feedback_text: 'test feedback',
    last_edit: '20. April 2022, 3 PM',
    pk: 1
  }
  const mockOnDelete = jest.fn()
  const tree = render(
    <ModerationFeedback
      feedback={mockProps}
      onDelete={mockOnDelete}
    />)
  const deleteButton = tree.container.querySelector('#delete-input')
  fireEvent.click(deleteButton)
  expect(mockOnDelete).toHaveBeenCalled()
})

test('ModerationFeedback onEdit', () => {
  const mockProps = {
    feedback_text: 'test feedback',
    last_edit: '20. April 2022, 3 PM',
    pk: 1
  }
  const mockOnEdit = jest.fn()
  const tree = render(
    <ModerationFeedback
      feedback={mockProps}
      onEdit={mockOnEdit}
    />)
  const editButton = tree.container.querySelector('#edit-input')
  fireEvent.click(editButton)
  expect(mockOnEdit).toHaveBeenCalled()
})
