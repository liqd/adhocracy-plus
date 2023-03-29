import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import { HoverButton } from '../HoverButton'

test('Show button with normal text', () => {
  render(
    <HoverButton
      textMouseOff="activated"
    />
  )
  expect(screen.getByText('activated')).toBeInTheDocument()
})

test('Show button with hover text, via mouse', () => {
  render(
    <HoverButton
      textMouseOn="deactivate"
      textMouseOff="activated"
    />
  )
  fireEvent.mouseOver(screen.getByText('activated'))
  expect(screen.getByText('deactivate')).toBeInTheDocument()
  fireEvent.mouseOut(screen.getByText('deactivate'))
  expect(screen.getByText('activated')).toBeInTheDocument()
})

test('Show button with hover text, via keyboard', () => {
  render(
    <HoverButton
      textMouseOn="deactivate"
      textMouseOff="activated"
    />
  )
  fireEvent.focus(screen.getByText('activated'))
  expect(screen.getByText('deactivate')).toBeInTheDocument()
  fireEvent.blur(screen.getByText('deactivate'))
  expect(screen.getByText('activated')).toBeInTheDocument()
})

test('Show button with normal text and click on button', () => {
  const onChangeFn = jest.fn()
  render(
    <HoverButton
      textMouseOn="deactivate"
      textMouseOff="activated"
      onClick={onChangeFn}
    />
  )
  expect(screen.getByText('activated')).toBeInTheDocument()
  fireEvent.click(screen.getByText('activated'))
  expect(onChangeFn).toHaveBeenCalled()
})
