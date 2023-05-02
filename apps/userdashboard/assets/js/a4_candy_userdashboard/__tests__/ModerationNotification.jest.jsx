import React from 'react'
import { render, fireEvent, screen, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { ModerationNotification } from '../ModerationNotification'

/** MOCK DEFINITIONS START **/

const mockedNotification = {
  comment: 'example comment text',
  comment_url: '/liqd-orga/ideas/2022-00001/?comment=2',
  feedback_api_url: '/api/comments/2/moderatorfeedback/',
  is_blocked: false,
  is_moderator_marked: false,
  is_modified: true,
  is_unread: true,
  last_edit: '5. Dezember 2022, 15:38',
  moderator_feedback: null,
  num_reports: 1,
  pk: 2,
  user_image: '/static/images/avatar-02.svg',
  user_name: 'user',
  user_profile_url: '/profile/user/'
}

/** MOCK DEFINITIONS END **/

test('Render <ModerationNotification>', () => {
  render(
    <ModerationNotification
      notification={mockedNotification}
      getUrlParams={() => {}}
    />
  )
  const comment = screen.getByText(/example comment/)
  expect(comment).toBeTruthy()
})

test('showing "mark as read" alert', async () => {
  const mockedFn = jest.fn()
  const tree = render(
    <ModerationNotification
      notification={mockedNotification}
      getUrlParams={() => {}}
      loadData={mockedFn}
    />
  )
  const readButton = tree.container.querySelector('.dropdown-item')
  fireEvent.click(readButton)
  await waitFor(() => {
    const foundAlert = screen.getByText(/mock alert/)
    expect(foundAlert).toBeTruthy()
  })
})

test('showing blocked alert', async () => {
  const mockedFn = jest.fn()
  const tree = render(
    <ModerationNotification
      notification={mockedNotification}
      getUrlParams={() => {}}
      loadData={mockedFn}
    />
  )
  const blockButton = tree.container.querySelector(
    '#moderation-notification-actions-bar-button-block-2'
  )
  fireEvent.click(blockButton)
  await waitFor(() => {
    const foundAlert = screen.getByText(/mock alert/)
    expect(foundAlert).toBeTruthy()
  })
})

test('showing highlighted alert', async () => {
  const mockedFn = jest.fn()
  const tree = render(
    <ModerationNotification
      notification={mockedNotification}
      getUrlParams={() => {}}
      loadData={mockedFn}
    />
  )
  const highlightButton = tree.container.querySelector(
    '#moderation-notification-actions-bar-button-highlight-2'
  )
  fireEvent.click(highlightButton)
  await waitFor(() => {
    const foundAlert = screen.getByText(/mock alert/)
    expect(foundAlert).toBeTruthy()
  })
})
