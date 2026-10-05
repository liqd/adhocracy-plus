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
  (global as any).fetch = jest.fn(() =>
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

test('sorts projects by most recent', async () => {
  render(<ModerationProjects projectApiUrl="/api/userdashboard/moderationprojects/" />)
  await waitFor(() => expect(tileTitles()).toEqual(['Alpha', 'Beta']))

  fireEvent.change(screen.getByRole('combobox'), { target: { value: 'recent' } })

  await waitFor(() => {
    expect(tileTitles()).toEqual(['Beta', 'Alpha'])
  })
})
