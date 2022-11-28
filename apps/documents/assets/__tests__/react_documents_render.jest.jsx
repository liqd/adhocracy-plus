import '../../../../__mocks__/jsDomMock'
import '../../../../__mocks__/ckeditorMock'
import React from 'react'
import { render } from '@testing-library/react'
import '@testing-library/jest-dom'

import ChapterNavItem from '../ChapterNavItem.jsx'
import ParagraphForm from '../ParagraphForm.jsx'

// checking for simple element to see if component is rendered as interim solution

test('Chapter Nav Item is showing', () => {
  const tree = render(
    <ChapterNavItem />
  )
  const navItemBtn = tree.getElementsByClassName('commenting--toc__button')
  const navItemActionBtnGroup = tree.getElementsByClassName('commenting__actions')
  expect(navItemBtn).toBeInTheDocument()
  expect(navItemActionBtnGroup).toBeInTheDocument()
})

test('Paragraph Form is showing', () => {
  const tree = render(
    <ParagraphForm paragraph={{ name: 'test-paragraph' }} config={{ height: 500 }} />
  )
  const paragraphContainer = tree.getElementsByClassName('commenting__content--border')
  const paragraphTextarea = tree.getElementsByClassName('django-ckeditor-widget')
  const paragraphItemActionBtnGroup = tree.getElementsByClassName('commenting__actions')

  expect(paragraphContainer).toBeInTheDocument()
  expect(paragraphTextarea).toBeInTheDocument()
  expect(paragraphItemActionBtnGrou).toBeInTheDocument()
})
