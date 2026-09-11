import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'

let mockPollData: any = null
let mockSavedData: any = null
let mockChangeResponse: any = { questions: [] }
let mockChangeFails = false

const mockMakeDeferred = (result: any, fails: boolean, failArg?: any) => ({
  done (cb: (res: any) => void) {
    if (!fails) cb(result)
    return this
  },
  fail (cb: (arg: any) => void) {
    if (fails) cb(failArg)
    return this
  }
})

// the jest moduleNameMapper resolves every 'adhocracy4*' import to the same
// mock module, so all replacements have to happen in a single factory
jest.mock('adhocracy4', () => {
  const mockApi = function MockFormFieldError () {
    // doubles as the FormFieldError default export (renders nothing here)
    return null
  }
  mockApi.poll = {
    get: jest.fn(() => mockMakeDeferred(mockPollData, false)),
    change: jest.fn(() => (
      mockChangeFails
        ? mockMakeDeferred(null, true, { responseText: JSON.stringify(mockChangeResponse) })
        : mockMakeDeferred(mockSavedData, false)
    ))
  }
  return {
    __esModule: true,
    default: mockApi,
    alert: function MockAlert (props: any) {
      // a react component may return a plain string
      return props.message || null
    },
    updateDashboard: jest.fn()
  }
})

jest.mock('../../react_polls/components/UppyQuestionImageUpload', () => ({
  __esModule: true,
  default: function MockImageUpload () {
    return null
  }
}))

import api from 'adhocracy4/adhocracy4/static/api'
import { PollManagement } from '../components/PollManagement'
import { resetLocalKeys } from '../utils'

const choiceQuestion = {
  id: 1,
  label: 'First question',
  help_text: '',
  multiple_choice: false,
  is_open: false,
  is_confidential: false,
  choices: [
    { id: 10, label: 'A', is_other_choice: false },
    { id: 11, label: 'B', is_other_choice: false }
  ],
  userChoices: [],
  answers: [],
  image_url: null,
  totalVoteCount: 0
}

const openQuestion = {
  id: 2,
  label: 'Second question',
  help_text: 'an explanation',
  multiple_choice: false,
  is_open: true,
  is_confidential: false,
  choices: [],
  userChoices: [],
  answers: [],
  image_url: null
}

describe('PollManagement', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    resetLocalKeys()
    mockChangeFails = false
    mockPollData = {
      allow_unregistered_users: false,
      hide_results_until_finished: false,
      questions: [choiceQuestion, openQuestion]
    }
    mockSavedData = {
      allow_unregistered_users: false,
      hide_results_until_finished: false,
      questions: [choiceQuestion, openQuestion]
    }
    mockChangeResponse = { questions: [{ label: ['Please provide a question.'] }, {}] }
  })

  const renderManagement = (props = {}) => render(
    <PollManagement
      pollId={1}
      enableUnregisteredUsers
      questionImagesEnabled={false}
      {...props}
    />
  )

  it('renders the questions as a collapsed list', async () => {
    renderManagement()
    expect(await screen.findByText('First question')).toBeInTheDocument()
    expect(screen.getByText('Second question')).toBeInTheDocument()
    expect(screen.getByText('Question 1')).toBeInTheDocument()
    expect(screen.getByText('Question 2')).toBeInTheDocument()
    // collapsed: no editor fields visible
    expect(screen.queryByText('Question 1 of 2')).not.toBeInTheDocument()
  })

  it('expands a question when clicked and collapses on cancel', async () => {
    renderManagement()
    fireEvent.click(await screen.findByText('First question'))
    expect(screen.getByText('Question 1 of 2')).toBeInTheDocument()

    const textarea = screen.getByRole('textbox', { name: /Question/ })
    fireEvent.change(textarea, { target: { value: 'Edited' } })

    fireEvent.click(screen.getByText('Cancel'))
    expect(screen.queryByText('Question 1 of 2')).not.toBeInTheDocument()
    // the label was reverted to the snapshot
    expect(screen.getByText('First question')).toBeInTheDocument()
  })

  const clickItemSave = () => {
    const button = document.querySelector('.poll-management__editor-actions .btn--primary') as HTMLElement
    fireEvent.click(button)
  }

  it('keeps edits local when saving a single item', async () => {
    renderManagement()
    fireEvent.click(await screen.findByText('First question'))
    fireEvent.change(screen.getByRole('textbox', { name: /Question/ }), { target: { value: 'Edited' } })
    clickItemSave()

    expect(screen.queryByText('Question 1 of 2')).not.toBeInTheDocument()
    expect(screen.getByText('Edited')).toBeInTheDocument()
    expect(api.poll.change).not.toHaveBeenCalled()
  })

  it('navigates between questions with the arrows', async () => {
    renderManagement()
    fireEvent.click(await screen.findByText('First question'))
    fireEvent.click(screen.getByLabelText('Next question'))
    expect(screen.getByText('Question 2 of 2')).toBeInTheDocument()
    expect(screen.getByRole('textbox', { name: /Question/ })).toHaveValue('Second question')
  })

  it('adds a new open question and expands it', async () => {
    const { container } = renderManagement()
    await screen.findByText('First question')
    fireEvent.click(screen.getByText('New question'))
    fireEvent.click(screen.getByText('Open question'))

    expect(screen.getByText('Question 3 of 3')).toBeInTheDocument()
    expect(container.querySelectorAll('.poll-management__list-item')).toHaveLength(3)
  })

  it('deletes a question', async () => {
    renderManagement()
    await screen.findByText('First question')
    fireEvent.click(screen.getAllByLabelText('Delete question')[0])

    expect(screen.queryByText('First question')).not.toBeInTheDocument()
    expect(screen.getByText('Question 1')).toBeInTheDocument()
    expect(screen.getByText('Second question')).toBeInTheDocument()
  })

  it('sends the full payload on save and strips read-only fields', async () => {
    renderManagement()
    await screen.findByText('First question')
    fireEvent.click(screen.getByRole('button', { name: 'Save' }))

    expect(api.poll.change).toHaveBeenCalledTimes(1)
    const [payload, pollId] = (api.poll.change as jest.Mock).mock.calls[0]
    expect(pollId).toBe(1)
    expect(payload.allow_unregistered_users).toBe(false)
    expect(payload.hide_results_until_finished).toBe(false)
    expect(payload.questions).toHaveLength(2)
    expect(payload.questions[0]).toEqual({
      id: 1,
      label: 'First question',
      help_text: '',
      multiple_choice: false,
      is_open: false,
      is_confidential: false,
      choices: [
        { id: 10, label: 'A', is_other_choice: false },
        { id: 11, label: 'B', is_other_choice: false }
      ],
      image_alt_text: ''
    })
    expect(payload.questions[0].userChoices).toBeUndefined()
    expect(payload.questions[0].answers).toBeUndefined()
    expect(payload.questions[0].image_url).toBeUndefined()
  })

  it('shows an alert and expands the question with errors on failed save', async () => {
    mockChangeFails = true
    renderManagement()
    await screen.findByText('First question')
    fireEvent.click(screen.getByRole('button', { name: 'Save' }))

    expect(await screen.findByText('The poll could not be updated. Please check the data you entered again.')).toBeInTheDocument()
    expect(screen.getByText('Question 1 of 2')).toBeInTheDocument()
  })

  it('toggles the unregistered users option', async () => {
    renderManagement()
    const checkbox = await screen.findByLabelText('Allow unregistered users to vote')
    fireEvent.click(checkbox)
    expect(checkbox).toBeChecked()
  })

  it('collapses an expanded question when its row is clicked again', async () => {
    const { container } = renderManagement()
    fireEvent.click(await screen.findByText('First question'))
    expect(screen.getByText('Question 1 of 2')).toBeInTheDocument()

    fireEvent.click(container.querySelector('.poll-management__summary') as HTMLElement)
    expect(screen.queryByText('Question 1 of 2')).not.toBeInTheDocument()
  })

  it('reorders questions via drag and drop', async () => {
    const { container } = renderManagement()
    await screen.findByText('First question')

    const items = container.querySelectorAll('.poll-management__item')
    expect(items).toHaveLength(2)

    fireEvent.dragStart(items[0])
    fireEvent.dragEnter(items[1])
    fireEvent.dragOver(items[1])
    fireEvent.drop(items[1])
    fireEvent.dragEnd(items[0])

    expect(screen.getByText('Question 1')).toBeInTheDocument()
    // after the drop the second question is first in the list
    const labels = Array.from(container.querySelectorAll('.poll-management__label')).map((el) => el.textContent)
    expect(labels[0]).toBe('Second question')
  })
})
