import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'

import PollAnswerReview from '../components/PollAnswerReview'

describe('PollAnswerReview', () => {
  const questions = [
    {
      id: 1,
      label: 'Pick one',
      multiple_choice: false,
      is_open: false,
      is_confidential: false,
      choices: [
        { id: 10, label: 'Red', is_other_choice: false },
        { id: 11, label: 'Blue', is_other_choice: false }
      ],
      userChoices: [11]
    }
  ]

  it('renders the info banner', () => {
    render(<PollAnswerReview questions={questions} onChangeAnswer={jest.fn()} />)
    expect(
      screen.getByText(
        'Thank you for taking part in the poll! You will see the results as soon as the participation phase is over.'
      )
    ).toBeInTheDocument()
  })

  it('renders choices without percentages', () => {
    const { container } = render(<PollAnswerReview questions={questions} onChangeAnswer={jest.fn()} />)
    expect(screen.getByText('Red')).toBeInTheDocument()
    expect(screen.getByText('Blue')).toBeInTheDocument()
    expect(container.querySelector('.poll-choice__percentage')).not.toBeInTheDocument()
  })

  it('renders the change answers button', () => {
    render(<PollAnswerReview questions={questions} onChangeAnswer={jest.fn()} />)
    expect(screen.getByText('Change my answers')).toBeInTheDocument()
  })

  it('dismisses the info banner when the close button is clicked', () => {
    render(<PollAnswerReview questions={questions} onChangeAnswer={jest.fn()} />)
    const banner = screen.getByText(
      'Thank you for taking part in the poll! You will see the results as soon as the participation phase is over.'
    )
    expect(banner).toBeInTheDocument()
    fireEvent.click(screen.getByTestId('alert'))
    expect(banner).not.toBeInTheDocument()
  })
})
