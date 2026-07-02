const React = require('react')

module.exports = {
  __esModule: true,

  // Default export used by default imports (QuestionImage, Alert, api, etc.)
  default: function (props) {
    if (props && props.imageUrl) {
      return React.createElement('div', { className: 'mock-question-image', 'data-prop-alt': props.alt || '' },
        React.createElement('img', { className: 'mock-question-image-img', src: props.imageUrl, alt: props.alt })
      )
    }
    if (props && props.message) {
      return React.createElement('div', { 'data-testid': 'alert', onClick: props.onClick }, props.message || props.children || null)
    }
    return null
  },

  // Named exports used by existing moderation tests
  alert: function () { return 'mock alert' },
  widget: function () { return null },

  // Named exports used by polls
  PollOpenQuestion: function (props) {
    return React.createElement('div', { 'data-testid': 'poll-open-question' })
  },
  ConfidentialNotice: function () {
    return React.createElement('div', { 'data-testid': 'confidential-notice' })
  },
  TextareaWithCounter: function (props) {
    return React.createElement('textarea', { 'data-testid': 'textarea-with-counter', value: props.value, onChange: props.onChange, disabled: props.disabled })
  },
  TermsOfUseCheckbox: function () {
    return React.createElement('div', { 'data-testid': 'terms-of-use-checkbox' })
  },
  Alert: function (props) {
    return React.createElement('div', { 'data-testid': 'alert', onClick: props.onClick }, props.message || props.children || null)
  }
}
