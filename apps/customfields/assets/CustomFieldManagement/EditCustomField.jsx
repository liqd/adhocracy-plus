/* eslint-disable camelcase */
import React from 'react'
import django from 'django'

const TRANSLATED = {
  question: django.gettext('Question'),
  required: django.gettext('Question is required'),
  openQuestion: django.gettext('Open-ended question'),
  answer: django.pgettext('noun', 'Answer'),
  addAnswer: django.gettext('Add answer'),
  delete: django.gettext('Delete')
}

export const EditCustomField = (props) => {
  const isChoice = props.field.type === 'choice'
  return (
    <section className="editpoll__question-container custom-fields__field">
      <div className="editpoll__question">
        <div className="form-group editpoll__question--border custom-fields__card">
          <div className="custom-fields__card-header">
            <h3 className="custom-fields__card-title">{props.title}</h3>
            <button
              type="button"
              className="custom-fields__delete"
              onClick={props.onDelete}
              title={TRANSLATED.delete}
            >
              <i className="fas fa-trash-alt" aria-label={TRANSLATED.delete} />
            </button>
          </div>

          <label htmlFor={'id_custom_fields-' + props.id + '-label'}>
            {TRANSLATED.question}
          </label>
          <input
            id={'id_custom_fields-' + props.id + '-label'}
            type="text"
            value={props.field.label}
            onChange={(e) => { props.onLabelChange(e.target.value) }}
          />

          <div className="custom-fields__options">
            <div className="form-check">
              <label
                className="form-check__label"
                htmlFor={'id_custom_fields-' + props.id + '-required'}
              >
                <input
                  type="checkbox"
                  id={'id_custom_fields-' + props.id + '-required'}
                  checked={props.field.required || false}
                  onChange={(e) => { props.onRequiredChange(e.target.checked) }}
                />
                &nbsp;
                {TRANSLATED.required}
              </label>
            </div>
            <div className="form-check">
              <label
                className="form-check__label"
                htmlFor={'id_custom_fields-' + props.id + '-open'}
              >
                <input
                  type="checkbox"
                  id={'id_custom_fields-' + props.id + '-open'}
                  checked={!isChoice}
                  onChange={(e) => { props.onTypeChange(e.target.checked ? 'open' : 'choice') }}
                />
                &nbsp;
                {TRANSLATED.openQuestion}
              </label>
            </div>
          </div>

          {isChoice &&
            <div className="custom-fields__answers">
              {props.field.choices.map((choice, index) => {
                const key = choice.id || choice.key
                return (
                  <div className="form-group" key={key}>
                    <label htmlFor={'id_custom_fields-' + props.id + '-choices-' + index}>
                      {TRANSLATED.answer} {index + 1}
                    </label>
                    <div className="input-group custom-fields__input-group">
                      <input
                        id={'id_custom_fields-' + props.id + '-choices-' + index}
                        type="text"
                        className="input-group__input"
                        value={choice.label}
                        onChange={(e) => { props.onChoiceLabelChange(index, e.target.value) }}
                      />
                      <button
                        className="custom-fields__answer-delete"
                        onClick={() => props.onDeleteChoice(index)}
                        title={TRANSLATED.delete}
                        type="button"
                      >
                        <i className="fa fa-times" aria-label={TRANSLATED.delete} />
                      </button>
                    </div>
                  </div>
                )
              })}
              <button
                type="button"
                className="btn custom-fields__add-answer"
                onClick={props.onAppendChoice}
              >
                <i className="fa fa-plus" aria-hidden="true" />
                {TRANSLATED.addAnswer}
              </button>
            </div>}
        </div>
      </div>
    </section>
  )
}
