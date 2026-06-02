/**
 * Maps CKEditor fontSize presets (default / big / huge) to semantic headings.
 * Loaded on dashboard pages only (see init_dashboard.js).
 */
const FONT_SIZE_TO_HEADING = {
  default: 'paragraph',
  big: 'heading3',
  huge: 'heading2',
}

const FONT_SIZE_OPTIONS = new Set(Object.keys(FONT_SIZE_TO_HEADING))

function configUsesFontSizeHeadings (config) {
  const options = config?.fontSize?.options
  if (!Array.isArray(options)) {
    return false
  }
  return options.some(
    (option) => typeof option === 'string' && FONT_SIZE_OPTIONS.has(option)
  )
}

function bridgeFontSizeToHeadings (editor) {
  if (editor._fontSizeHeadingBridge) {
    return
  }
  const fontSize = editor.commands.get('fontSize')
  const heading = editor.commands.get('heading')
  if (!fontSize || !heading) {
    return
  }
  editor._fontSizeHeadingBridge = true

  fontSize.on(
    'execute',
    (evt, data) => {
      const value = data.value
      if (!FONT_SIZE_OPTIONS.has(value)) {
        return
      }
      evt.stop()
      editor.execute('heading', { value: FONT_SIZE_TO_HEADING[value] })
    },
    { priority: 'highest' }
  )
}

function patchClassicEditorCreate () {
  const OriginalEditor = window.ClassicEditor
  if (!OriginalEditor || OriginalEditor._fontSizeHeadingPatched) {
    return
  }
  OriginalEditor._fontSizeHeadingPatched = true
  const originalCreate = OriginalEditor.create.bind(OriginalEditor)
  OriginalEditor.create = function (element, config) {
    return originalCreate(element, config).then((editor) => {
      if (configUsesFontSizeHeadings(config)) {
        bridgeFontSizeToHeadings(editor)
      }
      return editor
    })
  }
}

function wrapRegisterCallback () {
  const previousRegister = window.ckeditorRegisterCallback
  if (typeof previousRegister !== 'function' || previousRegister._fontSizeHeadingWrapped) {
    return
  }
  function wrappedRegister (id, callback) {
    previousRegister(id, function (editor) {
      bridgeFontSizeToHeadings(editor)
      if (callback) {
        callback(editor)
      }
    })
  }
  wrappedRegister._fontSizeHeadingWrapped = true
  window.ckeditorRegisterCallback = wrappedRegister
}

function setupExistingEditors () {
  Object.values(window.editors || {}).forEach(bridgeFontSizeToHeadings)
}

function waitForClassicEditor (callback, attemptsLeft = 40) {
  if (window.ClassicEditor) {
    callback()
    return
  }
  if (attemptsLeft <= 0) {
    return
  }
  window.setTimeout(() => waitForClassicEditor(callback, attemptsLeft - 1), 50)
}

export function initCkeditorFontSizeAsHeadings () {
  if (!document.querySelector('.django_ckeditor_5')) {
    return
  }

  waitForClassicEditor(() => {
    patchClassicEditorCreate()
    wrapRegisterCallback()
    setupExistingEditors()
  })
}
