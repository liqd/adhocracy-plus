// checking for simple element to see if component is rendered as interim solution
import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'

// component to be tested
import QuestionModerator from '../QuestionModerator.jsx'

test('Question Moderator component is showing', () => {
  render(<QuestionModerator likes="1" />)
  const question = screen.getByTestId('question-moderator')
  expect(question).toBeInTheDocument()
})
