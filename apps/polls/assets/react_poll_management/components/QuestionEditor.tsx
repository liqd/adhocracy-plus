// apps/polls/assets/react_poll_management/components/QuestionEditor.tsx
import React, { useState } from 'react'
import django from 'django'

import FormFieldError from 'adhocracy4/adhocracy4/static/FormFieldError'
import UppyQuestionImageUpload from '../../react_polls/components/UppyQuestionImageUpload'

import type { ChoiceErrors, ManagementQuestion, QuestionErrors } from '../types'

const TRANSLATED = {
  question: django.gettext('Question'),
  questionOfTotal: django.gettext('Question %(number)s of %(total)s'),
  previous: django.gettext('Previous question'),
  next: django.gettext('Next question'),
  save: django.gettext('Save'),
  cancel: django.gettext('Cancel'),
  questionLabel: django.gettext('Question'),
  answerType: django.gettext('Answer type'),
  singleChoice: django.gettext('Single choice'),
  multipleChoice: django.gettext('Multiple choice'),
  confidential: django.gettext('Do not display answers publicly'),
  answer: django.pgettext('noun', 'Answer'),
  other: django.gettext('Other'),
  remove: django.gettext('remove'),
  addAnswer: django.gettext('Answer option'),
  addOpenAnswer: django.gettext('Open answer'),
  addExplanation: django.gettext('Explanation'),
  explanation: django.gettext('Explanation')
}

interface QuestionEditorProps {
  question: ManagementQuestion
  index: number
  total: number
  errors: QuestionErrors
  questionImagesEnabled: boolean
  onLabelChange: (label: string) => void
  onHelpTextChange: (helpText: string) => void
  onConfidentialChange: (value: boolean) => void
  onMultipleChoiceChange: (value: boolean) => void
  onImageChange: (base64: string) => void
  onAltTextChange: (altText: string) => void
  onChoiceLabelChange: (choiceIndex: number, label: string) => void
  onChoiceDelete: (choiceIndex: number) => void
  onChoiceAppend: () => void
  onOtherChoiceToggle: () => void
  onNavigate: (direction: -1 | 1) => void
  onSave: () => void
  onCancel: () => void
}

export const QuestionEditor = (props: QuestionEditorProps) => {
  const {
    question,
    index,
    total,
    errors,
    questionImagesEnabled,
    onNavigate,
    onSave,
    onCancel
  } = props

  const [hasHelptext, setHasHelptext] = useState(Boolean(question.help_text))
  const hasOtherOption = question.choices.some((choice) => choice.is_other_choice)
  const regularChoices = question.choices.filter((choice) => !choice.is_other_choice)

  return (
    <section className="poll-management__editor">
      <header className="poll-management__editor-header">
        <h3 className="poll-management__editor-title">
          {django.interpolate(TRANSLATED.questionOfTotal, { number: index + 1, total }, true)}
        </h3>
        <div className="btn-group poll-management__editor-nav" role="group">
          <button
            type="button"
            className="btn poll-management__nav-button"
            onClick={() => onNavigate(-1)}
            disabled={index === 0}
            title={TRANSLATED.previous}
            aria-label={TRANSLATED.previous}
          >
            <i className="fa fa-chevron-left" aria-hidden="true" />
          </button>
          <button
            type="button"
            className="btn poll-management__nav-button"
            onClick={() => onNavigate(1)}
            disabled={index === total - 1}
            title={TRANSLATED.next}
            aria-label={TRANSLATED.next}
          >
            <i className="fa fa-chevron-right" aria-hidden="true" />
          </button>
        </div>
        <div className="poll-management__editor-actions">
          <button type="button" className="btn btn--primary" onClick={onSave}>
            {TRANSLATED.save}
          </button>
          <button type="button" className="btn btn--light" onClick={onCancel}>
            {TRANSLATED.cancel}
          </button>
        </div>
      </header>

      <div className="form-group">
        <label htmlFor={`id_questions-${question.key}-name`}>
          {TRANSLATED.questionLabel}
          {question.id && (
            <span className="editpoll__help-text"> Id: Q{question.id}</span>
          )}
          <textarea
            id={`id_questions-${question.key}-name`}
            name={`questions-${question.key}-name`}
            value={question.label}
            onChange={(e) => props.onLabelChange(e.target.value)}
            aria-invalid={errors.label ? 'true' : 'false'}
            aria-describedby={errors.label ? `id_error-${question.key}` : undefined}
          />
        </label>
        <FormFieldError id={`id_error-${question.key}`} error={errors} field="label" />
      </div>

      {questionImagesEnabled && (
        <UppyQuestionImageUpload
          id={question.key}
          question={question}
          onImageChange={props.onImageChange}
          errors={errors}
          helpText={question.image_help_text}
          altText={question.image_alt_text}
          onAltTextChange={props.onAltTextChange}
        />
      )}

      <div className="form-check poll-management__confidential">
        <label
          className="form-check__label"
          htmlFor={`id_questions-${question.key}-is_confidential`}
        >
          <input
            type="checkbox"
            id={`id_questions-${question.key}-is_confidential`}
            name={`questions-${question.key}-is_confidential`}
            checked={question.is_confidential || false}
            onChange={(e) => props.onConfidentialChange(e.target.checked)}
          />
          &nbsp;
          {TRANSLATED.confidential}
        </label>
      </div>

      {!question.is_open && (
        <fieldset className="poll-management__answer-type">
          <legend>{TRANSLATED.answerType}</legend>
          <div className="form-check">
            <label
              className="form-check__label"
              htmlFor={`id_questions-${question.key}-single_choice`}
            >
              <input
                type="radio"
                id={`id_questions-${question.key}-single_choice`}
                name={`answer-type-${question.key}`}
                checked={!question.multiple_choice}
                onChange={() => props.onMultipleChoiceChange(false)}
              />
              &nbsp;
              {TRANSLATED.singleChoice}
            </label>
          </div>
          <div className="form-check">
            <label
              className="form-check__label"
              htmlFor={`id_questions-${question.key}-multiple_choice`}
            >
              <input
                type="radio"
                id={`id_questions-${question.key}-multiple_choice`}
                name={`answer-type-${question.key}`}
                checked={question.multiple_choice}
                onChange={() => props.onMultipleChoiceChange(true)}
              />
              &nbsp;
              {TRANSLATED.multipleChoice}
            </label>
          </div>
        </fieldset>
      )}

      {!question.is_open && (
        <div className="poll-management__answers">
          <h4 className="poll-management__answers-title">{TRANSLATED.answer}</h4>
          {question.choices.map((choice, choiceIndex) => {
            const choiceErrors: ChoiceErrors = errors.choices?.[choiceIndex] || {}
            if (choice.is_other_choice) {
              return (
                <div key={choice.key} className="poll-management__choice form-group">
                  <div>
                    {TRANSLATED.other}
                    {choice.id && (
                      <span className="editpoll__help-text"> Id: A{choice.id}</span>
                    )}
                  </div>
                  <div className="input-group">
                    <input
                      type="text"
                      className="input-group__input"
                      value={TRANSLATED.other}
                      disabled
                      aria-label={TRANSLATED.other}
                    />
                    <span className="input-group__after">
                      <button
                        type="button"
                        className="btn poll-management__choice-delete"
                        onClick={props.onOtherChoiceToggle}
                        title={TRANSLATED.remove}
                      >
                        <i className="fa fa-times" aria-label={TRANSLATED.remove} />
                      </button>
                    </span>
                  </div>
                </div>
              )
            }
            return (
              <div key={choice.key} className="poll-management__choice form-group">
                <label htmlFor={`id_choices-${choice.key}-name`}>
                  {`${TRANSLATED.answer} #${regularChoices.findIndex((regular) => regular.key === choice.key) + 1}`}
                  {choice.id && (
                    <span className="editpoll__help-text"> Id: A{choice.id}</span>
                  )}
                </label>
                <div className="input-group">
                  <input
                    id={`id_choices-${choice.key}-name`}
                    name={`choices-${choice.key}-name`}
                    type="text"
                    className="input-group__input"
                    value={choice.label}
                    onChange={(e) => props.onChoiceLabelChange(choiceIndex, e.target.value)}
                    aria-invalid={choiceErrors.label ? 'true' : 'false'}
                  />
                  <span className="input-group__after">
                    <button
                      type="button"
                      className="btn poll-management__choice-delete"
                      onClick={() => props.onChoiceDelete(choiceIndex)}
                      disabled={question.choices.length < 3}
                      title={TRANSLATED.remove}
                    >
                      <i className="fa fa-times" aria-label={TRANSLATED.remove} />
                    </button>
                  </span>
                </div>
                <FormFieldError
                  id={`id_error-choice-${choice.key}`}
                  error={choiceErrors}
                  field="label"
                />
              </div>
            )
          })}

          <div className="poll-management__buttons">
            <button
              type="button"
              className="btn poll-management__btn"
              onClick={props.onChoiceAppend}
            >
              <i className="fa fa-plus" aria-hidden="true" />
              {' '}
              {TRANSLATED.addAnswer}
            </button>
            <button
              type="button"
              className={`btn poll-management__btn ${hasOtherOption ? 'poll-management__btn--active' : ''}`}
              onClick={props.onOtherChoiceToggle}
              aria-pressed={hasOtherOption}
            >
              <i className={`fa ${hasOtherOption ? 'fa-check' : 'fa-plus'}`} aria-hidden="true" />
              {' '}
              {TRANSLATED.addOpenAnswer}
            </button>
          </div>
        </div>
      )}

      <div className="poll-management__buttons">
        <button
          type="button"
          className={`btn poll-management__btn ${hasHelptext ? 'poll-management__btn--active' : ''}`}
          onClick={() => setHasHelptext(!hasHelptext)}
          aria-pressed={hasHelptext}
        >
          <i className={`fa ${hasHelptext ? 'fa-check' : 'fa-plus'}`} aria-hidden="true" />
          {' '}
          {TRANSLATED.addExplanation}
        </button>
      </div>

      {hasHelptext && (
        <div className="form-group poll-management__explanation">
          <label htmlFor={`id_helptext-${question.key}-name`}>
            {TRANSLATED.explanation}
            <textarea
              id={`id_helptext-${question.key}-name`}
              name={`helptext-${question.key}-name`}
              value={question.help_text}
              onChange={(e) => props.onHelpTextChange(e.target.value)}
              aria-invalid={errors.help_text ? 'true' : 'false'}
              aria-describedby={errors.help_text ? `id_error-help-${question.key}` : undefined}
            />
          </label>
          <FormFieldError
            id={`id_error-help-${question.key}`}
            error={errors}
            field="help_text"
          />
        </div>
      )}
    </section>
  )
}
