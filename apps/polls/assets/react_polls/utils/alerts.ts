import django from 'django'
import type { AlertState } from '../types'

export const ALERT_SUCCESS: AlertState = {
  type: 'success',
  message: django.gettext('Your answer has been saved.')
}

export const ALERT_ERROR: AlertState = {
  type: 'danger',
  message: django.gettext('Your answer could not be saved. Please check the data you entered again.')
}

export const ALERT_INVALID: AlertState = {
  type: 'danger',
  message: django.gettext('Please answer the question before proceeding.')
}

export const ALERT_INCOMPLETE: AlertState = {
  type: 'warning',
  message: django.gettext('Please answer all questions before submitting.')
}

export const ALERT_CAPTCHA_INCOMPLETE: AlertState = {
  type: 'danger',
  message: django.gettext('Please complete the captcha before submitting.')
}
