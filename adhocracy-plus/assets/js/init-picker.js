import django from 'django'
import flatpickr from 'flatpickr'
import { German } from 'flatpickr/dist/l10n/de.js'
import { Russian } from 'flatpickr/dist/l10n/ru.js'
import { Dutch } from 'flatpickr/dist/l10n/nl.js'
import English from 'flatpickr/dist/l10n/default.js'

// Helper to link start and end date pickers
function linkPair (startPicker, endPicker) {
  const selectedDate = startPicker.selectedDates[0]
  if (selectedDate) {
    endPicker.set(
      'minDate',
      startPicker.formatDate(selectedDate, startPicker.config.dateFormat)
    )
  }
  startPicker.config.onChange.push((selectedDates, dateStr) => {
    if (selectedDates[0] > endPicker.selectedDates[0]) endPicker.clear()
    endPicker.set('minDate', dateStr)
  })

  endPicker.config.onChange.push((selectedDates, dateStr) => {
    if (selectedDates[0] < startPicker.selectedDates[0]) startPicker.clear()
    startPicker.set('maxDate', dateStr)
  })
}

// Initializes linked date pickers for start and end date fields
function linkDatePickers (flatpickrsMap) {
  const singlePhaseIds = ['id_start_date_date', 'id_end_date_date']
  const multiPhaseIds = [
    'id_phase_set-0-start_date_date',
    'id_phase_set-0-end_date_date',
    'id_phase_set-1-start_date_date',
    'id_phase_set-1-end_date_date',
    'id_phase_set-2-start_date_date',
    'id_phase_set-2-end_date_date'
  ]

  // Link single-phase pickers
  const startPicker = flatpickrsMap.get(singlePhaseIds[0])
  const endPicker = flatpickrsMap.get(singlePhaseIds[1])
  if (startPicker && endPicker) linkPair(startPicker, endPicker)

  // Link multi-phase pickers in pairs
  for (let i = 0; i < multiPhaseIds.length - 1; i += 2) {
    const phaseStartPicker = flatpickrsMap.get(multiPhaseIds[i])
    const phaseEndPicker = flatpickrsMap.get(multiPhaseIds[i + 1])
    if (phaseStartPicker && phaseEndPicker) { linkPair(phaseStartPicker, phaseEndPicker) }
  }
}

// Returns the appropriate language object based on the document language
function getLanguage () {
  const languages = { de: German, nl: Dutch, ru: Russian }
  return languages[document.documentElement.lang] || English
}

// Initializes all date and time pickers on the page
function initDatePicker () {
  const lang = getLanguage()
  const dateFormat = django
    .get_format('DATE_INPUT_FORMATS')[0]
    .replaceAll('%', '')
  const flatpickrsMap = new Map()

  // Initialize date pickers
  document.querySelectorAll('.datepicker').forEach((element) => {
    element.classList.add('form-control')
    const datePicker = flatpickr(element, { dateFormat, locale: lang })
    flatpickrsMap.set(element.id, datePicker)
  })

  // Link date pickers if needed
  linkDatePickers(flatpickrsMap)

  // Initialize time pickers
  document.querySelectorAll('.timepicker').forEach((element) => {
    const timePicker = flatpickr(element, {
      defaultHour: element.id.endsWith('start_date_time') ? '00' : '23',
      defaultMinute: element.id.endsWith('start_date_time') ? '00' : '59',
      dateFormat: 'H:i',
      enableTime: true,
      noCalendar: true,
      time_24hr: true,
      locale: lang
    })
    flatpickrsMap.set(element.id, timePicker)
  })
}

document.addEventListener('DOMContentLoaded', initDatePicker, false)
