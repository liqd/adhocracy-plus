import React from 'react'
import { render, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import { ModerationNotificationActionsBar } from '../ModerationNotificationActionsBar'

test('Unread has three buttons', () => {
  const tree = render(
    <ModerationNotificationActionsBar />
  )
  const buttons = tree.container.querySelectorAll('button')
  expect(buttons.length).toBe(3)
})

test('Unread with reply button changing to edit button', () => {
  const tree = render(
    <ModerationNotificationActionsBar
      isEditing
    />
  )
  const editIcon = tree.container.querySelector('.fa-pen')
  expect(editIcon).toBeTruthy()
})

test('Unread with highlight button disabled', () => {
  const tree = render(
    <ModerationNotificationActionsBar
      isBlocked
      isHighlighted={false}
      itemPk={7}
    />
  )
  const button =
    tree.container.querySelector('#moderation-notification-actions-bar-button-highlight-7')
  expect(button).toBeDisabled()
})

test('Unread with blocked button disabled', () => {
  const tree = render(
    <ModerationNotificationActionsBar
      isBlocked={false}
      isHighlighted
      itemPk={7}
    />
  )
  const button =
    tree.container.querySelector('#moderation-notification-actions-bar-button-block-7')
  expect(button).toBeDisabled()
})

test('Unread is highlighted', () => {
  const tree = render(
    <ModerationNotificationActionsBar
      isHighlighted
    />
  )
  const buttons = tree.container.querySelectorAll('button')
  expect(buttons.length).toBe(3)
})

test('Unread clicks: reply --> highlight --> block', () => {
  const mockToggleFn = jest.fn()
  const tree = render(
    <ModerationNotificationActionsBar
      isBlocked={false}
      isHighlighted={false}
      onToggleForm={mockToggleFn}
      onToggleBlock={mockToggleFn}
      onToggleHighlight={mockToggleFn}
      itemPk={7}
    />
  )
  const replyButton =
    tree.container.querySelector('#moderation-notification-actions-bar-button-reply-7')!
  const highlightButton =
    tree.container.querySelector('#moderation-notification-actions-bar-button-highlight-7')!
  const blockButton =
    tree.container.querySelector('#moderation-notification-actions-bar-button-block-7')!

  fireEvent.click(replyButton)
  fireEvent.click(highlightButton)
  fireEvent.click(blockButton)
  expect(mockToggleFn).toHaveBeenCalledTimes(3)
})

test('Read has three buttons', () => {
  const tree = render(
    <ModerationNotificationActionsBar />
  )
  const buttons = tree.container.querySelectorAll('button')
  expect(buttons.length).toBe(3)
})
