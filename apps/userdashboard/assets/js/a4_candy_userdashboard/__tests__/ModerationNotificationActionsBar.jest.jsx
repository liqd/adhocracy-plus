import React from 'react'
import { render, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import { ModerationNotificationActionsBar } from '../ModerationNotificationActionsBar'

test('Unread has three buttons', () => {
  const mockUnread = true
  const tree = render(
    <ModerationNotificationActionsBar
      isUnread={mockUnread}
    />
  )
  const buttons = tree.container.querySelectorAll('button')
  expect(buttons.length).toBe(3)
})

test('Unread with reply button changing to edit button', () => {
  const mockUnread = true
  const mockEditing = true
  const tree = render(
    <ModerationNotificationActionsBar
      isUnread={mockUnread}
      isEditing={mockEditing}
    />
  )
  const editIcon = tree.container.querySelector('.fa-pen')
  expect(editIcon).toBeTruthy()
})

test('Unread with highlight button disabled', () => {
  const mockUnread = true
  const mockBlocked = true
  const mockHighlighted = false
  const tree = render(
    <ModerationNotificationActionsBar
      isUnread={mockUnread}
      isBlocked={mockBlocked}
      isHighlighted={mockHighlighted}
      itemPk={7}
    />
  )
  const button =
    tree.container.querySelector('#moderation-notification-actions-bar-button-highlight-7')
  expect(button).toBeDisabled()
})

test('Unread with blocked button disabled', () => {
  const mockUnread = true
  const mockBlocked = false
  const mockHighlighted = true
  const tree = render(
    <ModerationNotificationActionsBar
      isUnread={mockUnread}
      isBlocked={mockBlocked}
      isHighlighted={mockHighlighted}
      itemPk={7}
    />
  )
  const button =
    tree.container.querySelector('#moderation-notification-actions-bar-button-block-7')
  expect(button).toBeDisabled()
})

test('Unread is highlighted', () => {
  const mockUnread = true
  const mockHighlighted = true
  const tree = render(
    <ModerationNotificationActionsBar
      isUnread={mockUnread}
      isHighlighted={mockHighlighted}
    />
  )
  const buttons = tree.container.querySelectorAll('button')
  expect(buttons.length).toBe(3)
})

test('Unread clicks: reply --> highlight --> block', () => {
  const mockUnread = true
  const mockDisabled = false
  const mockBlocked = false
  const mockHighlighted = false
  const mockToggleFn = jest.fn()
  const tree = render(
    <ModerationNotificationActionsBar
      isUnread={mockUnread}
      isDisabled={mockDisabled}
      isBlocked={mockBlocked}
      isHighlighted={mockHighlighted}
      onToggleForm={mockToggleFn}
      onToggleBlock={mockToggleFn}
      onToggleHighlight={mockToggleFn}
      itemPk={7}
    />
  )
  const replyButton =
    tree.container.querySelector('#moderation-notification-actions-bar-button-reply-7')
  const highlightButton =
    tree.container.querySelector('#moderation-notification-actions-bar-button-highlight-7')
  const blockButton =
    tree.container.querySelector('#moderation-notification-actions-bar-button-block-7')

  fireEvent.click(replyButton)
  fireEvent.click(highlightButton)
  fireEvent.click(blockButton)
  expect(mockToggleFn).toHaveBeenCalledTimes(3)
})

test('Read has three buttons', () => {
  const mockUnread = false
  const tree = render(
    <ModerationNotificationActionsBar
      isUnread={mockUnread}
    />
  )
  const buttons = tree.container.querySelectorAll('button')
  expect(buttons.length).toBe(3)
})
