import { Modal } from 'bootstrap'

jest.mock('bootstrap', () => ({
  Dropdown: { getOrCreateInstance: jest.fn() },
  Modal: { getOrCreateInstance: jest.fn() }
}))

function clickTrigger () {
  document.getElementById('trigger').dispatchEvent(
    new MouseEvent('click', { bubbles: true, cancelable: true })
  )
}

describe('auth modal', () => {
  let ajax
  let modalInstance

  beforeAll(async () => {
    // The module attaches its listeners on import, so the modal must exist.
    document.body.innerHTML = `
      <div class="modal" id="auth-modal">
        <div class="modal-body" id="auth-modal-body"></div>
      </div>`
    await import('./auth_modal.js')
  })

  beforeEach(() => {
    document.body.innerHTML = `
      <div class="modal" id="auth-modal">
        <div class="modal-body" id="auth-modal-body"></div>
      </div>
      <a id="trigger" href="/accounts/login/?next=/foo/">Log in</a>
    `
    ajax = jest.fn()
    modalInstance = { show: jest.fn() }
    window.htmx = { ajax }
    Modal.getOrCreateInstance.mockReturnValue(modalInstance)
  })

  afterEach(() => {
    delete window.htmx
    jest.clearAllMocks()
  })

  it('loads the login view into the modal via htmx', () => {
    clickTrigger()

    expect(ajax).toHaveBeenCalledWith('GET', '/accounts/login/?next=/foo/', {
      target: '#auth-modal-body',
      swap: 'innerHTML'
    })
    expect(modalInstance.show).toHaveBeenCalled()
  })

  it('leaves non auth links alone', () => {
    document.getElementById('trigger').setAttribute('href', '#section')
    clickTrigger()

    expect(ajax).not.toHaveBeenCalled()
    expect(modalInstance.show).not.toHaveBeenCalled()
  })
})
