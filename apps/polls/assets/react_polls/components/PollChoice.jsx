// apps/polls/assets/react_polls/components/PollChoice.jsx
import React, { useState, useEffect } from 'react'
import django from 'django'
import { ChoiceRow } from './ChoiceRow'
import { ConfidentialNotice } from 'adhocracy4/adhocracy4/polls/static/PollDetail/ConfidentialNotice'
import QuestionImage from 'adhocracy4/adhocracy4/polls/static/PollDetail/QuestionImage'

const translated = {
  multiple: django.gettext('Multiple answers are possible.')
}

const getOtherChoiceAnswer = (question) => {
  const userAnswerId = question.other_choice_user_answer
  return question.other_choice_answer ||
    (userAnswerId && question.other_choice_answers?.find(
      oc => oc.vote_id === userAnswerId
    )?.answer) || ''
}

export const PollChoice = ({ question, allowUnregisteredUsers, onAnswerChange, errors }) => {
  const [userChoices, setUserChoices] = useState(question.userChoices || [])
  const [otherChoiceAnswer, setOtherChoiceAnswer] = useState(getOtherChoiceAnswer(question))

  const otherChoice = question.choices.find(c => c.is_other_choice)
  const canVote = question.authenticated || allowUnregisteredUsers

  useEffect(() => {
    setOtherChoiceAnswer(getOtherChoiceAnswer(question))
  }, [question.other_choice_answer, question.other_choice_user_answer])

  const handleChoiceChange = (choiceId) => {
    if (question.multiple_choice) {
      const newChoices = userChoices.includes(choiceId)
        ? userChoices.filter(id => id !== choiceId)
        : [...userChoices, choiceId]

      setUserChoices(newChoices)
      onAnswerChange(question.id, choiceId, 'multi')

      if (otherChoice && !newChoices.includes(otherChoice.id)) {
        setOtherChoiceAnswer('')
        onAnswerChange(question.id, '', 'other')
      }
    } else {
      setUserChoices([choiceId])
      onAnswerChange(question.id, choiceId, 'single')

      if (otherChoice && choiceId !== otherChoice.id) {
        setOtherChoiceAnswer('')
        onAnswerChange(question.id, '', 'other')
      }
    }
  }

  const handleOtherChange = (event) => {
    const answer = event.target.value
    setOtherChoiceAnswer(answer)
    onAnswerChange(question.id, answer, 'other')
  }

  return (
    <div className="poll poll--question">
      <fieldset>
        <legend className="poll__question-legend">
          <span className="poll__question-label">{question.label}</span>
        </legend>

        {question.image_url && <QuestionImage imageUrl={question.image_url} alt={question.image_alt_text || question.label} />}

        {question.help_text && (
          <div className="poll__help-text">{question.help_text}</div>
        )}

        {question.multiple_choice && (
          <div className="poll__help-text">{translated.multiple}</div>
        )}

        {question.is_confidential && <ConfidentialNotice />}

        <div className="poll__rows">
          {question.choices.map((choice) => (
            <ChoiceRow
              key={choice.id}
              choice={choice}
              checked={userChoices.includes(choice.id)}
              onInputChange={() => handleChoiceChange(choice.id)}
              type={question.multiple_choice ? 'checkbox' : 'radio'}
              disabled={!canVote}
              otherChoiceAnswer={otherChoiceAnswer}
              onOtherChange={handleOtherChange}
              errors={errors}
              name={question.multiple_choice ? undefined : `question-${question.id}`}
            />
          ))}
        </div>
      </fieldset>
    </div>
  )
}
