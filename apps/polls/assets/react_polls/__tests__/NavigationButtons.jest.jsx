import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'

import NavigationButtons from '../components/NavigationButtons'

describe('NavigationButtons', () => {
  const defaults = {
    onBack: jest.fn(),
    onSkip: jest.fn(),
    onNext: jest.fn(),
    onSubmit: jest.fn(),
    isLoading: false,
    isLastQuestion: false,
    currentIndex: 0
  }

  it('disables Back on first question', () => {
    render(<NavigationButtons {...defaults} currentIndex={0} />)
    expect(screen.getByText('Go Back')).toBeDisabled()
  })

  it('enables Back after first question', () => {
    render(<NavigationButtons {...defaults} currentIndex={1} />)
    expect(screen.getByText('Go Back')).not.toBeDisabled()
  })

  it('shows Skip and Next on non-last question', () => {
    render(<NavigationButtons {...defaults} isLastQuestion={false} />)
    expect(screen.getByText('Skip')).toBeInTheDocument()
    expect(screen.getByText('Next')).toBeInTheDocument()
    expect(screen.queryByText('Submit All')).not.toBeInTheDocument()
  })

  it('shows Submit All on last question and hides Skip/Next', () => {
    render(<NavigationButtons {...defaults} isLastQuestion />)
    expect(screen.getByText('Submit All')).toBeInTheDocument()
    expect(screen.queryByText('Skip')).not.toBeInTheDocument()
    expect(screen.queryByText('Next')).not.toBeInTheDocument()
  })

  it('shows Submitting... and disables button when loading', () => {
    render(<NavigationButtons {...defaults} isLastQuestion isLoading />)
    expect(screen.getByText('Submitting...')).toBeDisabled()
  })

  it.each([
    ['Go Back', 'onBack', 1],
    ['Skip', 'onSkip', 0],
    ['Next', 'onNext', 0]
  ])('calls %s handler when %s clicked', (label, handler) => {
    const fn = jest.fn()
    render(<NavigationButtons {...defaults} currentIndex={1} {...{ [handler]: fn }} />)
    fireEvent.click(screen.getByText(label))
    expect(fn).toHaveBeenCalledTimes(1)
  })

  it('calls onSubmit when Submit All clicked', () => {
    const onSubmit = jest.fn()
    render(<NavigationButtons {...defaults} isLastQuestion onSubmit={onSubmit} />)
    fireEvent.click(screen.getByText('Submit All'))
    expect(onSubmit).toHaveBeenCalledTimes(1)
  })
})
