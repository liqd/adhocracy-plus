import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'

import StartScreen from '../components/StartScreen'

describe('StartScreen', () => {
  const baseProps = {
    totalQuestions: 2,
    totalParticipants: 5,
    isAuthenticated: true,
    allowUnregisteredUsers: false,
    hideResultsUntilFinished: false,
    manualLink: '',
    onStart: jest.fn(),
    onShowResults: jest.fn()
  }

  it('shows the results button by default', () => {
    render(<StartScreen {...baseProps} />)
    expect(screen.getByText('Show results')).toBeInTheDocument()
  })

  it('hides the results button when results are hidden until the phase ends', () => {
    render(<StartScreen {...baseProps} hideResultsUntilFinished />)
    expect(screen.queryByText('Show results')).not.toBeInTheDocument()
  })
})
