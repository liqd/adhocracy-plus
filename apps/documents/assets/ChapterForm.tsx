import React from 'react'
import FlipMove from 'react-flip-move'
import django from 'django'
import FormFieldError from 'adhocracy4/adhocracy4/static/FormFieldError'
import ParagraphForm from './ParagraphForm'
import type { Chapter } from './types'

interface ChapterFormProps {
  id: string
  chapter: Chapter
  errors?: Record<string, unknown> | null
  csrfCookieName?: string
  uploadUrl?: string
  uploadFileTypes?: string[]
  config?: Record<string, unknown>
  onChapterNameChange: (name: string) => void
  onParagraphNameChange: (paragraphIndex: number, name: string) => void
  onParagraphTextChange: (paragraphIndex: number, text: string) => void
  onParagraphAppend: () => void
  onParagraphMoveUp: (paragraphIndex: number) => void
  onParagraphMoveDown: (paragraphIndex: number) => void
  onParagraphDelete: (paragraphIndex: number) => void
  onParagraphAddBefore?: (paragraphIndex: number) => void
}

const ChapterForm = (props: ChapterFormProps) => {
  return (
    <section>
      <div className="commenting">
        <div className="form-group commenting__content">
          <label htmlFor={'id_chapters-' + props.id + '-name'}>
            {django.gettext('Chapter title')}
            <input
              id={'id_chapters-' + props.id + '-name'}
              name={'chapters-' + props.id + '-name'}
              type="text"
              value={props.chapter.name}
              onChange={(e) => { props.onChapterNameChange(e.target.value) }}
            />
          </label>
          <FormFieldError id={'id_error-' + props.id} error={props.errors} field="name" />
        </div>
      </div>

      <FlipMove easing="cubic-bezier(0.25, 0.5, 0.75, 1)">
        {
          props.chapter.paragraphs.map(function (paragraph, index, arr) {
            const key = paragraph.id || paragraph.key
            return (
              <div key={key}>
                <ParagraphForm
                  id={String(key)}
                  key={key}
                  index={index}
                  paragraph={paragraph}
                  csrfCookieName={props.csrfCookieName}
                  uploadUrl={props.uploadUrl}
                  uploadFileTypes={props.uploadFileTypes}
                  config={props.config}
                  onDelete={() => { props.onParagraphDelete(index) }}
                  onMoveUp={index !== 0 ? () => { props.onParagraphMoveUp(index) } : null}
                  onMoveDown={index < arr.length - 1 ? () => { props.onParagraphMoveDown(index) } : null}
                  onParagraphAddBefore={() => { props.onParagraphAddBefore?.(index) }}
                  onNameChange={(name) => { props.onParagraphNameChange(index, name) }}
                  onTextChange={(text) => { props.onParagraphTextChange(index, text) }}
                  errors={props.errors && props.errors.paragraphs ? (props.errors.paragraphs as Record<string, unknown>[])[index] : null}
                />
              </div>
            )
          })
        }
      </FlipMove>

      <button
        className="btn btn--light btn--small"
        onClick={props.onParagraphAppend}
        type="button"
      >
        <i className="fa fa-plus" /> {django.gettext('Add a new paragraph')}
      </button>
    </section>
  )
}

export default ChapterForm
