import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { ModerationStatement } from '../ModerationStatement'

test('ModerationStatement with optimal values', () => {
  const mockProps = {
    feedback_text: 'test statement',
    last_edit: '20. April 2022, 3 PM',
    pk: 1
  }
  render(
    <ModerationStatement statement={mockProps} />
  )
  const statement = screen.getByText('test statement')
  expect(statement).toBeTruthy()
})

test('ModerationStatement onDelete', () => {
  const mockProps = {
    feedback_text: 'test statement',
    last_edit: '20. April 2022, 3 PM',
    pk: 1
  }
  const mockOnDelete = jest.fn()
  const tree = render(
    <ModerationStatement
      statement={mockProps}
      onDelete={mockOnDelete}
      notificationIsPending
    />)
  const deleteButton = tree.container.querySelector('#delete-input')
  fireEvent.click(deleteButton)
  expect(mockOnDelete).toHaveBeenCalled()
})

test('ModerationStatement onEdit', () => {
  const mockProps = {
    feedback_text: 'test statement',
    last_edit: '20. April 2022, 3 PM',
    pk: 1
  }
  const mockOnEdit = jest.fn()
  const tree = render(
    <ModerationStatement
      statement={mockProps}
      onEdit={mockOnEdit}
      notificationIsPending
    />)
  const editButton = tree.container.querySelector('#edit-input')
  fireEvent.click(editButton)
  expect(mockOnEdit).toHaveBeenCalled()
})
