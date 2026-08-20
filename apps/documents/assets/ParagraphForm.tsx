import React, { useCallback, useEffect } from 'react'
import django from 'django'
import FormFieldError from 'adhocracy4/adhocracy4/static/FormFieldError'
import type { ChapterParagraph } from './types'

declare global {
  interface Window {
    ckeditorRegisterCallback: (id: string, cb: (editor: any) => void) => void
    ckeditorUnregisterCallback: (id: string) => void
    editors: Record<string, any>
  }
}

// translations
const translations = {
  headline: django.gettext('Headline'),
  paragraph: django.gettext('Paragraph'),
  moveUp: django.gettext('Move up'),
  moveDown: django.gettext('Move down'),
  delete: django.gettext('Delete'),
  helpText: django.gettext(
    'If you add an image, please provide an ' +
      'alternate text. It serves as a textual description of the image ' +
      'content and is read out by screen readers. Describe the image in ' +
      'approx. 80 characters. Example: A busy square with people in summer.'
  )
}

interface ParagraphFormProps {
  id: string
  index?: number
  paragraph: ChapterParagraph
  errors?: Record<string, unknown> | null
  onNameChange: (name: string) => void
  onTextChange: (text: string) => void
  onDelete?: () => void
  onMoveUp?: (() => void) | null
  onMoveDown?: (() => void) | null
  onParagraphAddBefore?: () => void
  uploadUrl?: string
  uploadFileTypes?: string[]
  csrfCookieName?: string
  config?: Record<string, unknown>
}

const ParagraphForm = (props: ParagraphFormProps) => {
  const { onTextChange: propsOnTextChange } = props
  const id = 'id_paragraphs-' + props.id
  const ckeditorId = id + '-text'

  const setDataHandler = useCallback((editor: any) => {
    editor.model.document.on('change:data', () => {
      propsOnTextChange(editor.getData())
    })
  }, [propsOnTextChange])

  useEffect(() => {
    window.ckeditorRegisterCallback(ckeditorId, setDataHandler)
    const editor = window.editors[ckeditorId]
    if (editor) {
      setDataHandler(editor)
    }
    return () => {
      window.ckeditorUnregisterCallback(ckeditorId)
    }
  }, [props.id, props.onTextChange, props.index, ckeditorId, setDataHandler])

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name = e.target.value
    props.onNameChange(name)
  }

  return (
    <section>
      <div className="row">
        <div className="col-lg-9">
          <div className="commenting__content--border">
            <div className="form-group">
              <label htmlFor={id + '-name'}>
                {translations.headline}
                <input
                  className="form-control"
                  id={id + '-name'}
                  name={'paragraphs-' + props.id + '-name'}
                  type="text"
                  value={props.paragraph.name}
                  onChange={handleNameChange}
                  aria-invalid={props.errors ? 'true' : 'false'}
                  aria-describedby={props.errors ? 'id_error-' + props.id : undefined}
                />
                <FormFieldError
                  id={'id_error-' + props.id}
                  error={props.errors}
                  field="name"
                />
              </label>
            </div>

            <div className="form-group">
              <label htmlFor={id + '-text'}>
                {translations.paragraph}
                <div
                  id={'id_paragraph-help-text-' + props.id}
                  className="form-hint"
                >
                  {translations.helpText}
                </div>
              </label>
              <div className="ck-editor-container">
                <textarea
                  id={ckeditorId}
                  className="django_ckeditor_5"
                  defaultValue={props.paragraph.text}
                />
                <div />
                <span
                  className="word-count"
                  id={ckeditorId + '_script-word-count'}
                />
                <input
                  type="hidden"
                  id={ckeditorId + '_script-ck-editor-5-upload-url'}
                  data-upload-url={props.uploadUrl}
                  data-upload-file-types={JSON.stringify(props.uploadFileTypes)}
                  data-csrf_cookie_name={props.csrfCookieName}
                />
                <span id={ckeditorId + '_script-span'}>
                  <script id={ckeditorId + '_script'} type="application/json">
                    {JSON.stringify(props.config)}
                  </script>
                </span>
              </div>
              <FormFieldError
                id={'id_error-' + props.id}
                error={props.errors}
                field="text"
              />
            </div>
          </div>
        </div>

        <div className="commenting__actions btn-group" role="group">
          <button
            className="btn btn--light btn--small"
            onClick={props.onMoveUp ?? undefined}
            disabled={!props.onMoveUp}
            title={translations.moveUp}
            type="button"
          >
            <i className="fa fa-chevron-up" aria-label={translations.moveUp} />
          </button>
          <button
            className="btn btn--light btn--small"
            onClick={props.onMoveDown ?? undefined}
            disabled={!props.onMoveDown}
            title={translations.moveDown}
            type="button"
          >
            <i
              className="fa fa-chevron-down"
              aria-label={translations.moveDown}
            />
          </button>
          <button
            className="btn btn--light btn--small"
            onClick={props.onDelete}
            title={translations.delete}
            type="button"
          >
            <i className="fas fa-trash-alt" aria-label={translations.delete} />
          </button>
        </div>
      </div>
    </section>
  )
}

export default ParagraphForm
