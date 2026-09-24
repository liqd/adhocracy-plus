import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'

jest.mock('../../react_polls/components/UppyQuestionImageUpload', () => ({
  __esModule: true,
  default: function MockImageUpload () {
    // a react component may return a plain string
    return 'mock-image-upload'
  }
}))

import { QuestionEditor } from '../components/QuestionEditor'
import type { ManagementQuestion } from '../types'

const question: ManagementQuestion = {
  id: 1,
  key: 'q_1',
  label: 'First question',
  help_text: '',
  multiple_choice: false,
  is_open: false,
  is_confidential: false,
  choices: [
    { id: 10, key: 'c_10', label: 'A', is_other_choice: false },
    { id: 11, key: 'c_11', label: 'B', is_other_choice: false }
  ]
}

const defaults = {
  index: 0,
  total: 3,
  errors: {},
  questionImagesEnabled: false,
  onLabelChange: jest.fn(),
  onHelpTextChange: jest.fn(),
  onConfidentialChange: jest.fn(),
  onMultipleChoiceChange: jest.fn(),
  onImageChange: jest.fn(),
  onAltTextChange: jest.fn(),
  onChoiceLabelChange: jest.fn(),
  onChoiceDelete: jest.fn(),
  onChoiceAppend: jest.fn(),
  onOtherChoiceToggle: jest.fn(),
  onNavigate: jest.fn(),
  onSave: jest.fn(),
  onCancel: jest.fn()
}

describe('QuestionEditor', () => {
  it('shows the question position within the poll', () => {
    render(<QuestionEditor question={question} {...defaults} index={1} />)
    expect(screen.getByText('Question 2 of 3')).toBeInTheDocument()
  })

  it('disables previous on first and next on last question', () => {
    const { rerender } = render(<QuestionEditor question={question} {...defaults} index={0} total={2} />)
    expect(screen.getByLabelText('Previous question')).toBeDisabled()
    expect(screen.getByLabelText('Next question')).not.toBeDisabled()

    rerender(<QuestionEditor question={question} {...defaults} index={1} total={2} />)
    expect(screen.getByLabelText('Previous question')).not.toBeDisabled()
    expect(screen.getByLabelText('Next question')).toBeDisabled()
  })

  it('navigates to the previous and next question', () => {
    const onNavigate = jest.fn()
    render(<QuestionEditor question={question} {...defaults} index={1} total={3} onNavigate={onNavigate} />)
    fireEvent.click(screen.getByLabelText('Previous question'))
    expect(onNavigate).toHaveBeenLastCalledWith(-1)
    fireEvent.click(screen.getByLabelText('Next question'))
    expect(onNavigate).toHaveBeenLastCalledWith(1)
  })

  it('collapses on save and reverts on cancel', () => {
    const onSave = jest.fn()
    const onCancel = jest.fn()
    render(<QuestionEditor question={question} {...defaults} onSave={onSave} onCancel={onCancel} />)
    fireEvent.click(screen.getByText('Save'))
    expect(onSave).toHaveBeenCalledTimes(1)
    fireEvent.click(screen.getByText('Cancel'))
    expect(onCancel).toHaveBeenCalledTimes(1)
  })

  it('changes the answer type between single and multiple choice', () => {
    const onMultipleChoiceChange = jest.fn()
    const { rerender } = render(<QuestionEditor question={question} {...defaults} onMultipleChoiceChange={onMultipleChoiceChange} />)
    fireEvent.click(screen.getByLabelText('Multiple choice'))
    expect(onMultipleChoiceChange).toHaveBeenCalledWith(true)

    rerender(<QuestionEditor question={{ ...question, multiple_choice: true }} {...defaults} onMultipleChoiceChange={onMultipleChoiceChange} />)
    fireEvent.click(screen.getByLabelText('Single choice'))
    expect(onMultipleChoiceChange).toHaveBeenCalledWith(false)
  })

  it('adds and toggles answer options', () => {
    const onChoiceAppend = jest.fn()
    const onOtherChoiceToggle = jest.fn()
    render(
      <QuestionEditor
        question={question}
        {...defaults}
        onChoiceAppend={onChoiceAppend}
        onOtherChoiceToggle={onOtherChoiceToggle}
      />
    )
    fireEvent.click(screen.getByText('Answer option'))
    expect(onChoiceAppend).toHaveBeenCalledTimes(1)
    fireEvent.click(screen.getByText('Open answer'))
    expect(onOtherChoiceToggle).toHaveBeenCalledTimes(1)
  })

  it('renders the other answer option as disabled input', () => {
    render(
      <QuestionEditor
        question={{
          ...question,
          choices: [...question.choices, { id: 12, key: 'c_12', label: 'other', is_other_choice: true }]
        }}
        {...defaults}
      />
    )
    const otherInput = screen.getByLabelText('Other') as HTMLInputElement
    expect(otherInput).toBeDisabled()
  })

  it('toggles the explanation field', () => {
    render(<QuestionEditor question={question} {...defaults} />)
    expect(screen.queryByRole('textbox', { name: 'Explanation' })).not.toBeInTheDocument()
    fireEvent.click(screen.getByText('Explanation'))
    expect(screen.getByRole('textbox', { name: 'Explanation' })).toBeInTheDocument()
  })

  it('shows explanation when the question already has one', () => {
    render(
      <QuestionEditor question={{ ...question, help_text: 'because' }} {...defaults} />
    )
    expect(screen.getByRole('textbox', { name: 'Explanation' })).toHaveValue('because')
  })

  it('hides answer options and answer type for open questions', () => {
    render(
      <QuestionEditor question={{ ...question, is_open: true, choices: [] }} {...defaults} />
    )
    expect(screen.queryByText('Answer option')).not.toBeInTheDocument()
    expect(screen.queryByLabelText('Multiple choice')).not.toBeInTheDocument()
    expect(screen.getByText('Explanation')).toBeInTheDocument()
  })
})
