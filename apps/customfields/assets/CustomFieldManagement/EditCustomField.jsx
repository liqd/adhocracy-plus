/* eslint-disable camelcase */
import React from 'react'
import django from 'django'
import FlipMove from 'react-flip-move'

const TRANSLATED = {
  question: django.gettext('Question'),
  answer: django.pgettext('noun', 'Answer'),
  required: django.gettext('This question is required'),
  newAnswer: django.gettext('New answer'),
  moveUp: django.gettext('Move up'),
  moveDown: django.gettext('Move down'),
  delete: django.gettext('Delete'),
  openQuestion: django.gettext('Open question'),
  multipleChoice: django.gettext('Multiple choice question')
}

export const EditCustomField = React.forwardRef((props, ref) => {
  const isChoice = props.field.type === 'choice'
  return (
    <section ref={ref} className="editpoll__question-container">
      <div className="editpoll__question">
        <div className="form-group editpoll__question--border">
          <label htmlFor={'id_custom_fields-' + props.id + '-label'}>
            {TRANSLATED.question}
            <span className="editpoll__help-text">
              {' '}·{' '}
              {isChoice ? TRANSLATED.multipleChoice : TRANSLATED.openQuestion}
            </span>
            <textarea
              id={'id_custom_fields-' + props.id + '-label'}
              name={'custom_fields-' + props.id + '-label'}
              value={props.field.label}
              onChange={(e) => { props.onLabelChange(e.target.value) }}
            />
          </label>

          <div className="form-check">
            <label
              className="form-check__label"
              htmlFor={'id_custom_fields-' + props.id + '-required'}
            >
              <input
                type="checkbox"
                id={'id_custom_fields-' + props.id + '-required'}
                name={'custom_fields-' + props.id + '-required'}
                checked={props.field.required || false}
                onChange={(e) => { props.onRequiredChange(e.target.checked) }}
              />
              &nbsp;
              {TRANSLATED.required}
            </label>
          </div>

          {isChoice &&
            <FlipMove easing="cubic-bezier(0.25, 0.5, 0.75, 1)">
              {props.field.choices.map((choice, index) => {
                const key = choice.id || choice.key
                return (
                  <div key={key}>
                    <div className="form-group">
                      <div>
                        {TRANSLATED.answer} {index + 1}
                      </div>
                      <div className="input-group">
                        <input
                          id={'id_custom_fields-' + props.id + '-choices-' + index}
                          type="text"
                          className="input-group__input"
                          value={choice.label}
                          onChange={(e) => { props.onChoiceLabelChange(index, e.target.value) }}
                        />
                        <button
                          className="input-group__after btn editpoll__btn--delete"
                          onClick={() => props.onDeleteChoice(index)}
                          title={TRANSLATED.delete}
                          type="button"
                        >
                          <i
                            className="fa fa-times"
                            aria-label={TRANSLATED.delete}
                          />
                        </button>
                      </div>
                    </div>
                  </div>
                )
              })}
            </FlipMove>}

          {isChoice &&
            <div className="editpoll__btns--question">
              <button
                className="btn editpoll__btn--question"
                onClick={props.onAppendChoice}
                type="button"
              >
                <i className="fa fa-plus" /> {TRANSLATED.newAnswer}
              </button>
            </div>}
        </div>
      </div>

      <div className="editpoll__question-actions btn-group" role="group">
        <button
          className="btn poll__btn--light"
          onClick={props.onMoveUp}
          disabled={!props.onMoveUp}
          title={TRANSLATED.moveUp}
          type="button"
        >
          <i
            className="fa fa-chevron-up"
            aria-label={TRANSLATED.moveUp}
          />
        </button>
        <button
          className="btn poll__btn--light"
          onClick={props.onMoveDown}
          disabled={!props.onMoveDown}
          title={TRANSLATED.moveDown}
          type="button"
        >
          <i
            className="fa fa-chevron-down"
            aria-label={TRANSLATED.moveDown}
          />
        </button>
        <button
          className="btn poll__btn--light"
          onClick={props.onDelete}
          title={TRANSLATED.delete}
          type="button"
        >
          <i
            className="fas fa-trash-alt"
            aria-label={TRANSLATED.delete}
          />
        </button>
      </div>
    </section>
  )
})

EditCustomField.displayName = 'EditCustomField'
