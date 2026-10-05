import React from 'react'
import { render, fireEvent, screen, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { ModerationNotification } from '../ModerationNotification'

/** MOCK DEFINITIONS START **/

const mockedNotification = {
  pk: 2,
  item_type: 'comment' as const,
  label: 'Comment',
  text: 'example comment text',
  title: null,
  url: '/liqd-orga/ideas/2022-00001/?comment=2',
  moderate_url: '',
  api_url: '/api/userdashboard/moderation/1/comments/2/',
  feedback_api_url: '/api/comments/2/moderatorfeedback/',
  is_blocked: false,
  is_moderator_marked: false,
  is_modified: true,
  is_unread: true,
  last_edit: '5. Dezember 2022, 15:38',
  moderator_feedback: null,
  num_reports: 1,
  user_image: '/static/images/avatar-02.svg',
  user_name: 'user',
  user_profile_url: '/profile/user/'
}

const mockedIdea = {
  pk: 5,
  item_type: 'idea' as const,
  label: 'Idea',
  text: 'example idea description',
  title: 'My idea title',
  url: '/liqd-orga/ideas/2022-00005/',
  moderate_url: '/liqd-orga/ideas/2022-00005/moderate/',
  api_url: '',
  feedback_api_url: '',
  is_blocked: false,
  is_moderator_marked: false,
  is_modified: false,
  is_unread: false,
  last_edit: '5. Dezember 2022, 15:38',
  moderator_feedback: null,
  num_reports: 0,
  user_name: 'user',
  user_profile_url: '/profile/user/'
}

/** MOCK DEFINITIONS END **/

test('renders an idea with label and moderation feedback link', () => {
  const tree = render(
    <ModerationNotification
      notification={mockedIdea}
      getUrlParams={() => ''}
    />
  )
  expect(screen.getByText(/example idea description/)).toBeTruthy()
  expect(screen.getByText('Idea')).toBeTruthy()
  const link = tree.container.querySelector(
    "a[href='/liqd-orga/ideas/2022-00005/moderate/']"
  )!
  expect(link).toBeTruthy()
  expect(link.textContent).toMatch(/Add feedback/i)
  expect(
    tree.container.querySelector('#moderation-notification-actions-bar-button-block-5')
  ).toBeNull()
})

test('Render <ModerationNotification>', () => {
  render(
    <ModerationNotification
      notification={mockedNotification}
      getUrlParams={() => ''}
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
      getUrlParams={() => ''}
      loadData={mockedFn}
    />
  )
  const readButton = tree.container.querySelector('.dropdown-item')!
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
      getUrlParams={() => ''}
      loadData={mockedFn}
    />
  )
  const blockButton = tree.container.querySelector(
    '#moderation-notification-actions-bar-button-block-2'
  )!
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
      getUrlParams={() => ''}
      loadData={mockedFn}
    />
  )
  const highlightButton = tree.container.querySelector(
    '#moderation-notification-actions-bar-button-highlight-2'
  )!
  fireEvent.click(highlightButton)
  await waitFor(() => {
    const foundAlert = screen.getByText(/mock alert/)
    expect(foundAlert).toBeTruthy()
  })
})
