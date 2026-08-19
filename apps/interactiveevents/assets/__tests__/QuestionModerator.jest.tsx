// checking for simple element to see if component is rendered as interim solution
import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'

// component to be tested
import QuestionModerator from '../QuestionModerator'

test('Question Moderator component is showing', () => {
  render(
    <QuestionModerator
      id={1}
      is_on_shortlist={false}
      is_live={false}
      is_hidden={false}
      is_answered={false}
      likes={{ count: 1, session_like: false }}
      updateQuestion={jest.fn()}
      removeFromList={jest.fn()}
    />
  )
  const question = screen.getByTestId('question-moderator')
  expect(question).toBeInTheDocument()
})
