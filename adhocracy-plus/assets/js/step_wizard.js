// Behaviour for client side multi step forms (e.g. the idea submission form).
//
// Progressive enhancement: the whole form is rendered in the DOM, marking each
// logical section with `data-step-wizard-step`. Without JavaScript all sections
// stay visible and the form submits as a whole. With JavaScript only the active
// section is shown and the "Next" button validates the current section before
// advancing.

// Hidden inputs are barred from constraint validation and widgets with a
// hidden native control (e.g. the CKEditor source textarea) are synced before
// validation, so the remaining fields can be checked even when their step is
// not the active one.
function isValidatable (field) {
  return typeof field.checkValidity === 'function' && field.type !== 'hidden'
}

function firstInvalidField (step) {
  const fields = step.querySelectorAll('input, select, textarea')
  return Array.from(fields).find(function (field) {
    return isValidatable(field) && !field.checkValidity()
  })
}

// Rich text editors keep their content in a separate model and only copy it
// back to the underlying textarea on submit. Sync it before validating so a
// required editor is checked against what the user actually typed.
function syncRichTextEditors (container) {
  const editors = window.editors
  if (!editors) {
    return
  }
  Object.keys(editors).forEach(function (id) {
    const editor = editors[id]
    if (
      editor &&
      editor.sourceElement &&
      container.contains(editor.sourceElement) &&
      typeof editor.updateSourceElement === 'function'
    ) {
      editor.updateSourceElement()
    }
  })
}

function focusStep (step) {
  const field = step.querySelector(
    'input:not([type="hidden"]):not([type="file"]):not([disabled]), ' +
    'select:not([disabled]), textarea:not([disabled])'
  )
  if (field) {
    field.focus()
  }
}

function reportField (field) {
  if (!field) {
    return
  }
  // Widgets such as CKEditor hide the native control, so report the error on
  // the visible editor and focus it.
  const container = field.closest('.ck-editor-container')
  const editable = container
    ? container.querySelector('.ck-editor__editable')
    : null
  if (editable) {
    field.setAttribute('aria-invalid', 'true')
    editable.setAttribute('aria-invalid', 'true')
    editable.focus()
    return
  }
  // Widgets such as select2 hide the native control, so reporting validity may
  // fail because the element is not focusable. Swallow that and fall back to
  // focusing whatever is visible.
  try {
    field.reportValidity()
  } catch {
    field.focus()
  }
}

function clearInvalid (step) {
  step.querySelectorAll('[aria-invalid="true"]').forEach(function (field) {
    field.removeAttribute('aria-invalid')
  })
}

function initStepWizard (form) {
  if (form.dataset.stepWizardInitialized) {
    return
  }

  const steps = Array.from(form.querySelectorAll('[data-step-wizard-step]'))
  if (steps.length < 2) {
    return
  }

  form.dataset.stepWizardInitialized = 'true'
  form.classList.add('step-wizard')

  const progress = form.querySelector('[data-step-wizard-progress]')
  const status = form.querySelector('[data-step-wizard-status]')
  const backButton = form.querySelector('[data-step-wizard-back]')
  const nextButton = form.querySelector('[data-step-wizard-next]')
  const submitButton = form.querySelector('[data-step-wizard-submit]')

  const total = steps.length
  let current = 0
  let dots = []

  // The number of rendered steps varies (optional steps may be omitted server
  // side), so build the progress dots from the actual steps.
  function buildProgress () {
    if (!progress) {
      return
    }
    progress.innerHTML = ''
    dots = []
    for (let index = 0; index < total; index++) {
      const dot = document.createElement('span')
      dot.className = 'step-wizard__dot'
      progress.appendChild(dot)
      dots.push(dot)
    }
  }

  function initialStep () {
    // After a server side validation error, jump to the first affected step.
    const errorIndex = steps.findIndex(function (step) {
      return step.querySelector('[role="alert"], .errorlist, [aria-invalid="true"]')
    })
    if (errorIndex > -1) {
      return errorIndex
    }
    const requested = parseInt(
      new URLSearchParams(window.location.search).get('step'),
      10
    )
    if (requested > 0 && requested <= total) {
      return requested - 1
    }
    return 0
  }

  function updateController () {
    if (backButton) {
      backButton.classList.toggle('d-none', current === 0)
    }
    if (nextButton) {
      nextButton.classList.toggle('d-none', current === total - 1)
    }
    if (submitButton) {
      submitButton.classList.toggle('d-none', current !== total - 1)
    }
  }

  function updateProgress () {
    dots.forEach(function (dot, index) {
      dot.classList.toggle('is-active', index <= current)
    })
    if (status) {
      const label = status.dataset.label || ''
      status.textContent = label
        .replace('%(current)s', String(current + 1))
        .replace('%(total)s', String(total))
    }
  }

  function render (moveFocus) {
    steps.forEach(function (step, index) {
      const active = index === current
      step.classList.toggle('d-none', !active)
    })
    updateController()
    updateProgress()
    if (moveFocus) {
      focusStep(steps[current])
      // Let layout dependent widgets (e.g. the map) recalculate their size now
      // that the step is visible.
      window.requestAnimationFrame(function () {
        window.dispatchEvent(new Event('resize'))
      })
    }
  }

  function goTo (index) {
    current = Math.min(Math.max(index, 0), total - 1)
    render(true)
  }

  function advance () {
    syncRichTextEditors(steps[current])
    const invalid = firstInvalidField(steps[current])
    if (invalid) {
      reportField(invalid)
      return
    }
    clearInvalid(steps[current])
    goTo(current + 1)
  }

  if (nextButton) {
    nextButton.addEventListener('click', advance)
  }
  if (backButton) {
    backButton.addEventListener('click', function () {
      goTo(current - 1)
    })
  }

  // The form is rendered with `novalidate`, so validate all steps before
  // submitting and surface the first invalid one.
  form.addEventListener('submit', function (event) {
    // Enter on an intermediate step should advance instead of submitting the
    // whole form.
    if (current !== total - 1) {
      event.preventDefault()
      advance()
      return
    }
    syncRichTextEditors(form)
    for (let index = 0; index < total; index++) {
      const invalid = firstInvalidField(steps[index])
      if (invalid) {
        event.preventDefault()
        current = index
        render(true)
        reportField(invalid)
        return
      }
    }
  })

  buildProgress()
  current = initialStep()
  render(false)
}

function init () {
  document.querySelectorAll('form[data-step-wizard]').forEach(initStepWizard)
}

// Hide the inactive steps only after the browser had a chance to run the other
// DOMContentLoaded handlers. Map widgets, for instance, measure their container
// on init and render the wrong extent when it is already hidden.
function scheduleInit () {
  if (typeof window.requestAnimationFrame === 'function') {
    window.requestAnimationFrame(function () {
      init()
    })
  } else {
    window.setTimeout(init, 0)
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', scheduleInit, false)
} else {
  scheduleInit()
}

document.addEventListener('a4.embed.ready', scheduleInit, false)

export { initStepWizard }
