import React from 'react'
import { render, screen, waitFor, fireEvent, cleanup } from '@testing-library/react'
import '@testing-library/jest-dom'
import ModerationProjects from '../ModerationProjects'

const projects = [
  {
    id: 1,
    title: 'Alpha',
    organisation: 'Org A',
    moderation_detail_url: '/moderation/detail/alpha/',
    num_unread_comments: 2,
    num_unread_items: 5,
    num_reported_unread_comments: 5,
    comment_count: 0,
    created: '2026-01-01T00:00:00Z',
    access: 1,
    tile_image: '',
    tile_image_copyright: ''
  },
  {
    id: 2,
    title: 'Beta',
    organisation: 'Org B',
    moderation_detail_url: '/moderation/detail/beta/',
    num_unread_comments: 0,
    num_unread_items: 0,
    num_reported_unread_comments: 0,
    comment_count: 0,
    created: '2026-02-01T00:00:00Z',
    access: 1,
    tile_image: '',
    tile_image_copyright: ''
  }
]

const tileTitles = () => Array.from(document.querySelectorAll('.tile__title')).map(el => el.textContent)

beforeEach(() => {
  window.history.replaceState({}, '', '/?status=all')
  ;(global as any).fetch = jest.fn(() =>
    Promise.resolve({ json: () => Promise.resolve(projects) })
  )
})

afterEach(() => {
  cleanup()
  window.history.replaceState({}, '', '/')
  jest.clearAllMocks()
})

test('filters projects by search query', async () => {
  render(<ModerationProjects projectApiUrl="/api/userdashboard/moderationprojects/" />)
  await waitFor(() => expect(tileTitles()).toHaveLength(2))

  fireEvent.change(screen.getByRole('searchbox'), { target: { value: 'Beta' } })

  await waitFor(() => {
    expect(tileTitles()).toEqual(['Beta'])
  })
})

test('shows the number of matching projects', async () => {
  render(<ModerationProjects projectApiUrl="/api/userdashboard/moderationprojects/" />)
  await waitFor(() => expect(tileTitles()).toHaveLength(2))

  expect(screen.getByText('2 Projects')).toBeTruthy()
})

test('filters projects by moderation status', async () => {
  window.history.replaceState({}, '', '/')
  render(<ModerationProjects projectApiUrl="/api/userdashboard/moderationprojects/" />)
  await waitFor(() => expect(tileTitles()).toEqual(['Alpha']))

  expect(screen.getByRole('button', { name: 'Open (01)' })).toHaveAttribute('aria-pressed', 'true')

  fireEvent.click(screen.getByRole('button', { name: 'Resolved (01)' }))

  await waitFor(() => {
    expect(tileTitles()).toEqual(['Beta'])
  })

  fireEvent.click(screen.getByRole('button', { name: 'All (02)' }))

  await waitFor(() => {
    expect(tileTitles()).toEqual(['Alpha', 'Beta'])
  })
})

test('sorts projects by newest first', async () => {
  render(<ModerationProjects projectApiUrl="/api/userdashboard/moderationprojects/" />)
  await waitFor(() => expect(tileTitles()).toEqual(['Alpha', 'Beta']))

  fireEvent.click(screen.getByRole('button', { name: 'Sort: Oldest First' }))
  fireEvent.click(screen.getByRole('button', { name: 'Newest First' }))

  await waitFor(() => {
    expect(tileTitles()).toEqual(['Beta', 'Alpha'])
  })
})
