const React = require('react')

const ModerationFeedback = (props) => React.createElement(
  'div',
  { className: 'mock-moderation-feedback' },
  props.feedback ? props.feedback.feedback_text : null
)

const ModerationFeedbackForm = () => React.createElement(
  'div',
  { className: 'mock-moderation-feedback-form' }
)

module.exports = {
  __esModule: true,
  default: 'mocked component',
  ModerationFeedback,
  ModerationFeedbackForm
}
