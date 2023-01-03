import django from 'django'
import flatpickr from 'flatpickr'

function initDatePicker () {
  const datepickers = document.querySelectorAll('.datepicker')
  const format = django.get_format('DATE_INPUT_FORMATS')[0].replaceAll('%', '')

  datepickers.forEach((e) => {
    e.classList.add('form-control')
    flatpickr(e, { dateFormat: format })
  })
}

document.addEventListener('DOMContentLoaded', initDatePicker, false)
