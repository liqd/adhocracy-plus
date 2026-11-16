import React from 'react'
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { ModerationIdeaFeedbackForm } from '../ModerationIdeaFeedbackForm'

const mockedItem = {
  pk: 7,
  item_type: 'idea' as const,
  label: 'Idea',
  text: '<p>An idea</p>',
  title: 'An idea',
  url: '/idea/7/',
  moderate_url: '',
  api_url: '/api/userdashboard/moderation/1/ideas/7/',
  feedback_api_url: '/api/userdashboard/moderation/1/ideas/7/feedback/',
  last_edit: 'now',
  is_modified: false,
  is_unread: true,
  is_blocked: false,
  is_moderator_marked: false,
  num_reports: 0,
  user_name: 'user',
  moderator_status: 'CONSIDERATION' as string | null,
  moderator_status_choices: [
    { value: 'CONSIDERATION', label: 'Under consideration' },
    { value: 'ACCEPTED', label: 'Accepted' }
  ]
}

let changeHandler: (() => void) | undefined
let currentData = '<p>initial feedback</p>'
const editableElement = { setAttribute: jest.fn() }
const fakeEditor = {
  getData: () => currentData,
  destroy: jest.fn(() => Promise.resolve()),
  model: {
    document: {
      on: jest.fn((_event: string, callback: () => void) => {
        changeHandler = callback
      })
    }
  },
  ui: {
    getEditableElement: () => editableElement
  }
}
const createEditor = jest.fn(() => Promise.resolve(fakeEditor))

beforeEach(() => {
  changeHandler = undefined
  currentData = '<p>initial feedback</p>'
  ;(window as any).ClassicEditor = { create: createEditor }
})

afterEach(() => {
  delete (window as any).ClassicEditor
  jest.clearAllMocks()
})

function renderForm (props = {}) {
  const onSubmit = jest.fn()
  const onCancel = jest.fn()
  const tree = render(
    <ModerationIdeaFeedbackForm
      item={mockedItem}
      ckeditorConfig={'{}'}
      onSubmit={onSubmit}
      onCancel={onCancel}
      {...props}
    />
  )
  return { ...tree, onSubmit, onCancel }
}

test('creates the rich text editor and labels the editable field', async () => {
  renderForm()

  await waitFor(() => expect(createEditor).toHaveBeenCalled())
  expect((createEditor.mock.calls[0] as any[])[1]).toEqual({ initialData: '' })
  expect(editableElement.setAttribute).toHaveBeenCalledWith(
    'id',
    'moderation-feedback-7-feedback'
  )
  expect(editableElement.setAttribute).toHaveBeenCalledWith(
    'aria-label',
    'Official feedback'
  )
})

test('submits the current editor content and status', async () => {
  const { onSubmit } = renderForm()
  await waitFor(() => expect(changeHandler).toBeDefined())

  currentData = '<p>changed feedback</p>'
  act(() => changeHandler?.())
  fireEvent.change(screen.getByLabelText('Processing status'), {
    target: { value: 'ACCEPTED' }
  })
  fireEvent.click(screen.getByRole('button', { name: 'Submit feedback' }))

  await waitFor(() => {
    expect(onSubmit).toHaveBeenCalledWith({
      feedback: '<p>changed feedback</p>',
      status: 'ACCEPTED'
    })
  })
})

test('destroys the editor on unmount', async () => {
  const { unmount } = renderForm()
  await waitFor(() => expect(createEditor).toHaveBeenCalled())

  unmount()

  expect(fakeEditor.destroy).toHaveBeenCalled()
})

test('uses the initial feedback as editor data', async () => {
  renderForm({
    initialFeedback: {
      pk: 3,
      feedback_text: '<p>existing feedback</p>',
      last_edit: 'now'
    }
  })

  await waitFor(() => expect(createEditor).toHaveBeenCalled())
  expect((createEditor.mock.calls[0] as any[])[1]).toEqual({
    initialData: '<p>existing feedback</p>'
  })
  expect(screen.getByRole('button', { name: 'Update feedback' })).toBeTruthy()
})

test('disables submit for feedback over the character limit', async () => {
  renderForm()
  await waitFor(() => expect(changeHandler).toBeDefined())

  currentData = '<p>' + 'a'.repeat(1001) + '</p>'
  act(() => changeHandler?.())

  expect(screen.getByRole('button', { name: 'Submit feedback' })).toBeDisabled()
  expect(screen.getByText(/1001\/1000/)).toBeTruthy()
})

test('calls onCancel without submitting', () => {
  const { onCancel, onSubmit } = renderForm()

  fireEvent.click(screen.getByRole('button', { name: 'Cancel' }))

  expect(onCancel).toHaveBeenCalled()
  expect(onSubmit).not.toHaveBeenCalled()
})

test('falls back to a textarea without the CKEditor bundle', async () => {
  delete (window as any).ClassicEditor
  const { onSubmit } = renderForm()

  fireEvent.change(screen.getByLabelText('Official feedback'), {
    target: { value: '<p>plain feedback</p>' }
  })
  fireEvent.click(screen.getByRole('button', { name: 'Submit feedback' }))

  await waitFor(() => {
    expect(onSubmit).toHaveBeenCalledWith({
      feedback: '<p>plain feedback</p>',
      status: 'CONSIDERATION'
    })
  })
})
