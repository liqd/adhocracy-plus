import React from 'react'
import { render, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import { ModerationNotificationActionsBar } from '../ModerationNotificationActionsBar'

test('Pending has three buttons', () => {
  const mockPending = true
  const tree = render(
    <ModerationNotificationActionsBar
      isPending={mockPending}
    />
  )
  const buttons = tree.container.querySelectorAll('button')
  expect(buttons.length).toBe(3)
})

test('Pending with reply button changing to edit button', () => {
  const mockPending = true
  const mockEditing = true
  const tree = render(
    <ModerationNotificationActionsBar
      isPending={mockPending}
      isEditing={mockEditing}
    />
  )
  const editIcon = tree.container.querySelector('.fa-pen')
  expect(editIcon).toBeTruthy()
})

test('Pending with highlight button disabled', () => {
  const mockPending = true
  const mockBlocked = true
  const mockHighlighted = false
  const tree = render(
    <ModerationNotificationActionsBar
      isPending={mockPending}
      isBlocked={mockBlocked}
      isHighlighted={mockHighlighted}
    />
  )
  const button =
    tree.container.querySelector('#moderation-notification-actions-bar-button-highlight')
  expect(button).toBeDisabled()
})

test('Pending with blocked button disabled', () => {
  const mockPending = true
  const mockBlocked = false
  const mockHighlighted = true
  const tree = render(
    <ModerationNotificationActionsBar
      isPending={mockPending}
      isBlocked={mockBlocked}
      isHighlighted={mockHighlighted}
    />
  )
  const button =
    tree.container.querySelector('#moderation-notification-actions-bar-button-block')
  expect(button).toBeDisabled()
})

test('Pending is highlighted', () => {
  const mockPending = true
  const mockHighlighted = true
  const tree = render(
    <ModerationNotificationActionsBar
      isPending={mockPending}
      isHighlighted={mockHighlighted}
    />
  )
  const buttons = tree.container.querySelectorAll('button')
  expect(buttons.length).toBe(3)
})

test('Pending clicks: reply --> highlight --> block', () => {
  const mockPending = true
  const mockDisabled = false
  const mockBlocked = false
  const mockHighlighted = false
  const mockToggleFn = jest.fn()
  const tree = render(
    <ModerationNotificationActionsBar
      isPending={mockPending}
      isDisabled={mockDisabled}
      isBlocked={mockBlocked}
      isHighlighted={mockHighlighted}
      onToggleForm={mockToggleFn}
      onToggleBlock={mockToggleFn}
      onToggleHighlight={mockToggleFn}
    />
  )
  const replyButton =
    tree.container.querySelector('#moderation-notification-actions-bar-button-reply')
  const highlightButton =
    tree.container.querySelector('#moderation-notification-actions-bar-button-highlight')
  const blockButton =
    tree.container.querySelector('#moderation-notification-actions-bar-button-block')

  fireEvent.click(replyButton)
  fireEvent.click(highlightButton)
  fireEvent.click(blockButton)
  expect(mockToggleFn).toHaveBeenCalledTimes(3)
})

test('Archived has one button', () => {
  const mockPending = false
  const tree = render(
    <ModerationNotificationActionsBar
      isPending={mockPending}
    />
  )
  const buttons = tree.container.querySelectorAll('button')
  expect(buttons.length).toBe(1)
})

test('Archived blocked shows blocked text', () => {
  const mockPending = false
  const mockBlocked = true
  const tree = render(
    <ModerationNotificationActionsBar
      isPending={mockPending}
      isBlocked={mockBlocked}
    />
  )
  const blockedTextDiv = tree.container.querySelector('.fw-bold')
  expect(blockedTextDiv).toBeTruthy()
})
