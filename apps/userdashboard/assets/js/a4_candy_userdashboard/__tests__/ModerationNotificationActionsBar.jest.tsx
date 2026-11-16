import React from 'react'
import { render, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import { ModerationNotificationActionsBar } from '../ModerationNotificationActionsBar'

test('shows give feedback, mark resolved and highlight', () => {
  const tree = render(
    <ModerationNotificationActionsBar
      isBlocked={false}
      isHighlighted={false}
      itemPk={7}
    />
  )

  const buttons = tree.container.querySelectorAll('button')
  expect(buttons.length).toBe(3)
  expect(
    tree.container.querySelector('#moderation-notification-comment-7-reply')
  ).toBeTruthy()
  expect(
    tree.container.querySelector('#moderation-notification-comment-7-resolve')
  ).toBeTruthy()
  expect(
    tree.container.querySelector('#moderation-notification-comment-7-highlight')
  ).toBeTruthy()
})

test('shows the pencil and edit label when feedback exists', () => {
  const tree = render(
    <ModerationNotificationActionsBar
      isEditing
      isBlocked={false}
      isHighlighted={false}
      itemPk={7}
    />
  )

  expect(tree.container.querySelector('.fa-pen')).toBeTruthy()
  expect(
    tree.container.querySelector('#moderation-notification-comment-7-reply')?.textContent
  ).toMatch(/Edit feedback/i)
})

test('shows hide from discussion for a highlighted comment', () => {
  const tree = render(
    <ModerationNotificationActionsBar
      isBlocked={false}
      isHighlighted
      itemPk={7}
    />
  )

  expect(
    tree.container.querySelector('#moderation-notification-comment-7-block')?.textContent
  ).toMatch(/Hide from discussion/i)
  expect(
    tree.container.querySelector('#moderation-notification-comment-7-highlight')
  ).toBeNull()
})

test('shows only reopen report for a hidden comment', () => {
  const tree = render(
    <ModerationNotificationActionsBar
      isBlocked
      isHighlighted={false}
      itemPk={7}
    />
  )

  const buttons = tree.container.querySelectorAll('button')
  expect(buttons.length).toBe(1)
  expect(
    tree.container.querySelector('#moderation-notification-comment-7-reopen')?.textContent
  ).toMatch(/Reopen report/i)
})

test('hides highlight and hide actions for ideas', () => {
  const tree = render(
    <ModerationNotificationActionsBar
      isBlocked={false}
      isHighlighted={false}
      itemPk={7}
      showModerationActions={false}
    />
  )

  expect(
    tree.container.querySelector('#moderation-notification-comment-7-highlight')
  ).toBeNull()
  expect(
    tree.container.querySelector('#moderation-notification-comment-7-block')
  ).toBeNull()
})

test('calls the action callbacks', () => {
  const onToggleForm = jest.fn()
  const onMarkResolved = jest.fn()
  const onToggleHighlight = jest.fn()
  const onToggleBlock = jest.fn()
  const onReopen = jest.fn()
  const tree = render(
    <ModerationNotificationActionsBar
      isBlocked={false}
      isHighlighted={false}
      itemPk={7}
      onToggleForm={onToggleForm}
      onMarkResolved={onMarkResolved}
      onToggleHighlight={onToggleHighlight}
      onToggleBlock={onToggleBlock}
      onReopen={onReopen}
    />
  )

  fireEvent.click(
    tree.container.querySelector('#moderation-notification-comment-7-reply')!
  )
  fireEvent.click(
    tree.container.querySelector('#moderation-notification-comment-7-resolve')!
  )
  fireEvent.click(
    tree.container.querySelector('#moderation-notification-comment-7-highlight')!
  )

  expect(onToggleForm).toHaveBeenCalled()
  expect(onMarkResolved).toHaveBeenCalled()
  expect(onToggleHighlight).toHaveBeenCalled()
})
