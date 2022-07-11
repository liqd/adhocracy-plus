window.CKEDITOR = {
  instances: [{}],
  replace: jest.fn(() => {
    return {
      on: jest.fn(),
      setData: jest.fn()
    }
  })
}
