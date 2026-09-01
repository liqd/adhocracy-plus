import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'

jest.mock('@uppy/core', () => {
  function MockUppy () {
    return {
      use: jest.fn(),
      on: jest.fn(),
      getPlugin: jest.fn(),
      getFiles: jest.fn(() => []),
      destroy: jest.fn()
    }
  }
  return { __esModule: true, default: MockUppy }
})
jest.mock('@uppy/dashboard', () => ({ __esModule: true, default: jest.fn() }))
jest.mock('@uppy/image-editor', () => ({ __esModule: true, default: jest.fn() }))

import UppyQuestionImageUpload from '../components/UppyQuestionImageUpload'

describe('UppyQuestionImageUpload', () => {
  const defaults = {
    id: 'q_1',
    onImageChange: jest.fn(),
    helpText: 'some hint',
    altText: '',
    onAltTextChange: jest.fn()
  }

  it('greys out the alt text field when no image is uploaded', () => {
    render(
      <UppyQuestionImageUpload
        {...defaults}
        question={{ image_url: null }}
      />
    )
    expect(screen.getByLabelText('Alt text')).toBeDisabled()
  })

  it('enables the alt text field when an image is uploaded', () => {
    render(
      <UppyQuestionImageUpload
        {...defaults}
        question={{ image_url: '/media/question.png' }}
      />
    )
    expect(screen.getByLabelText('Alt text')).toBeEnabled()
  })
})
