// ChoiceRow.tsx
import React, { useState, useEffect } from 'react'
import django from 'django'
import { TextareaWithCounter } from 'adhocracy4/adhocracy4/polls/static/PollDetail/TextareaWithCounter'
import type { PollChoiceData } from '../types'

const translated = {
  other: django.gettext('other')
}

interface ChoiceInputProps {
  type: string
  choice: PollChoiceData
  checked: boolean
  onInputChange: (event: React.ChangeEvent<HTMLInputElement>, isOtherChoice: boolean) => void
  disabled: boolean
  name?: string
  isResult?: boolean
}

const ChoiceInput = ({
  type,
  choice,
  checked,
  onInputChange,
  disabled,
  name,
  isResult = false // New prop for result mode
}: ChoiceInputProps) => (
  <div className="poll-choice__input-wrapper">
    {!isResult
      ? (
        <input
          className="poll-choice__input"
          type={type}
          id={'id_choice-' + choice.id + '-' + (type === 'radio' ? 'single' : 'multiple')}
          name={name}
          value={choice.id}
          checked={checked}
          onChange={(event) => onInputChange(event, choice.is_other_choice)}
          disabled={disabled}
          aria-describedby={'textarea-with-counter-' + choice.id}
        />
        )
      : (
        <div className="poll-choice__result-icon">
          {checked
            ? (
              <i className="fas fa-check-circle poll-choice__check-icon" />
              )
            : (
              <div className="poll-choice__empty-circle" />
              )}
        </div>
        )}
  </div>
)

interface ChoiceRowProps {
  choice: PollChoiceData
  checked: boolean
  onInputChange?: (event: React.ChangeEvent<HTMLInputElement>, isOtherChoice: boolean) => void
  type: string
  disabled?: boolean
  otherChoiceAnswer?: string
  onOtherChange?: (event: React.ChangeEvent<HTMLTextAreaElement>) => void
  errors?: unknown
  name?: string
  isResult?: boolean
  review?: boolean
  percent?: number | null
}

export const ChoiceRow = React.memo(({
  choice,
  checked,
  onInputChange,
  type,
  disabled,
  otherChoiceAnswer,
  onOtherChange,
  errors,
  name,
  isResult = false,
  review = false,
  percent = null
}: ChoiceRowProps) => {
  const [textareaValue, setTextareaValue] = useState(otherChoiceAnswer || '')
  const [showTextarea, setShowTextarea] = useState(false)

  useEffect(() => {
    // keep the textarea visibility in sync with the checked "other" choice
    /* eslint-disable react-hooks/set-state-in-effect */
    if (checked && choice.is_other_choice) {
      setShowTextarea(true)
    } else {
      setShowTextarea(false)
    }
    /* eslint-enable react-hooks/set-state-in-effect */
  }, [checked, choice.is_other_choice])

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>, isOtherChoice: boolean) => {
    if (isResult) return // No changes in result mode
    onInputChange?.(event, isOtherChoice)

    if (isOtherChoice && event.target.checked) {
      setShowTextarea(true)
    } else {
      setShowTextarea(false)
    }
  }

  const handleTextareaChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setTextareaValue(event.target.value)
    onOtherChange?.(event)
  }

  return (
    <label
      className={`poll-choice ${checked ? 'poll-choice--checked' : ''} ${choice.is_other_choice ? 'poll-choice--other' : ''} ${isResult ? 'poll-choice--result' : ''}${review ? ' poll-choice--review' : ''}`}
      htmlFor={!isResult ? ('id_choice-' + choice.id + '-' + (type === 'radio' ? 'single' : 'multiple')) : undefined}
    >
      {isResult && percent !== null && (
        <div
          className="poll-choice__fill"
          style={{ width: `${percent}%` }}
        />
      )}

      <div className="poll-choice__container">
        <ChoiceInput
          type={type}
          choice={choice}
          checked={checked}
          onInputChange={handleChange}
          disabled={disabled || isResult}
          name={name}
          isResult={isResult}
        />
        <span className="poll-choice__label">
          {choice.is_other_choice ? translated.other : choice.label}
        </span>
        {isResult && percent !== null && (
          <span className="poll-choice__percentage">{percent}%</span>
        )}
      </div>

      {showTextarea && !isResult && (
        <div className="poll-choice__textarea-container">
          <TextareaWithCounter
            id={choice.id}
            value={textareaValue}
            onChange={handleTextareaChange}
            disabled={disabled}
            error={errors}
            label={translated.other}
          />
        </div>
      )}
    </label>
  )
})

ChoiceRow.displayName = 'ChoiceRow'
