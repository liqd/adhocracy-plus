import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import { ModerationFeedback } from '../ModerationFeedback'

test('ModerationFeedback renders title, date and text', () => {
  const mockProps = {
    feedback_text: 'test feedback',
    last_edit: '20. April 2022, 3 PM',
    pk: 1
  }

  render(<ModerationFeedback feedback={mockProps} />)

  expect(screen.getByText('Moderator')).toBeTruthy()
  expect(screen.getByText('20. April 2022, 3 PM')).toBeTruthy()
  expect(screen.getByText('test feedback')).toBeTruthy()
})
