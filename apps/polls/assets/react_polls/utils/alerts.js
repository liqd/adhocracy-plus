// apps/polls/assets/react_polls/utils/alerts.js
import django from 'django'
export const ALERT_SUCCESS = {
  type: 'success',
  message: django.gettext('Your answer has been saved.')
}

export const ALERT_ERROR = {
  type: 'danger',
  message: django.gettext('Your answer could not be saved. Please check the data you entered again.')
}

export const ALERT_INVALID = {
  type: 'danger',
  message: django.gettext('Please answer the question before proceeding.')
}

export const ALERT_INCOMPLETE = {
  type: 'warning',
  message: django.gettext('Please answer all questions before submitting.')
}
