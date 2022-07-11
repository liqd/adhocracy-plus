// checking for simple element to see if component is rendered as interim solution
import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'

import ChapterNavItem from '../ChapterNavItem.jsx'
import ParagraphForm from '../ParagraphForm.jsx'

test('Chapter Nav Item is showing', () => {
  render(<ChapterNavItem />)
  const nav = screen.getByTestId('chapter-nav-item')
  expect(nav).toBeInTheDocument()
})

test('Paragraph Form is showing', () => {
  render(<ParagraphForm />)
  const nav = screen.getByTestId('paragraph-nav')
  expect(nav).toBeInTheDocument()
})
