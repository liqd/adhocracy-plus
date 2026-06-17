import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'

import { ChoiceRow } from '../components/ChoiceRow'

describe('ChoiceRow', () => {
  const baseChoice = { id: 1, label: 'Option A', is_other_choice: false }
  const otherChoice = { id: 2, label: 'other', is_other_choice: true }

  it('renders label', () => {
    render(
      <ChoiceRow
        choice={baseChoice} checked={false} type="radio"
        onInputChange={jest.fn()} onOtherChange={jest.fn()}
      />
    )
    expect(screen.getByText('Option A')).toBeInTheDocument()
  })

  it('shows checked state', () => {
    const { container } = render(
      <ChoiceRow
        choice={baseChoice} checked type="radio"
        onInputChange={jest.fn()} onOtherChange={jest.fn()}
      />
    )
    expect(container.querySelector('input[type="radio"]')).toBeChecked()
  })

  it('shows textarea for other when checked', () => {
    render(
      <ChoiceRow
        choice={otherChoice} checked type="radio"
        onInputChange={jest.fn()} onOtherChange={jest.fn()} otherChoiceAnswer=""
      />
    )
    expect(screen.getByTestId('textarea-with-counter')).toBeInTheDocument()
  })

  it('hides textarea for other when unchecked', () => {
    render(
      <ChoiceRow
        choice={otherChoice} checked={false} type="radio"
        onInputChange={jest.fn()} onOtherChange={jest.fn()}
      />
    )
    expect(screen.queryByTestId('textarea-with-counter')).not.toBeInTheDocument()
  })

  it('calls onOtherChange on textarea input', () => {
    const onOtherChange = jest.fn()
    render(
      <ChoiceRow
        choice={otherChoice} checked type="radio"
        onInputChange={jest.fn()} onOtherChange={onOtherChange} otherChoiceAnswer=""
      />
    )
    fireEvent.change(screen.getByTestId('textarea-with-counter'), { target: { value: 'x' } })
    expect(onOtherChange).toHaveBeenCalledTimes(1)
  })
})
