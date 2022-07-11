// checking for simple element to see if component is rendered as interim solution
import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'

// component to be tested
import ChapterNavItem from '../ChapterNavItem.jsx'

test('Chapter Nav is showing', () => {
  render(<ChapterNavItem />)
  const nav = screen.getByTestId('chapter-nav-item')
  expect(nav).toBeInTheDocument()
})
