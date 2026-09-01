// apps/polls/assets/react_poll_management/components/PollManagement.tsx
import React, { useEffect, useState } from 'react'
import django from 'django'

import api from 'adhocracy4/adhocracy4/static/api'
import { alert as Alert } from 'adhocracy4'
import { updateDashboard } from 'adhocracy4/adhocracy4/dashboard/assets/dashboard'

import { AddQuestionDropdown } from './AddQuestionDropdown'
import { QuestionEditor } from './QuestionEditor'
import { QuestionListItem } from './QuestionListItem'
import {
  buildQuestionsPayload,
  cloneQuestion,
  createEmptyChoice,
  createEmptyQuestion,
  moveItem,
  normalizeQuestion
} from '../utils'
import type {
  AlertValue,
  ManagementQuestion,
  PollManagementProps,
  QuestionErrors
} from '../types'

const TRANSLATED = {
  optionsTitle: django.gettext('Options'),
  allowUnregisteredUsersLabel: django.gettext('Allow unregistered users to vote'),
  allowUnregisteredUsersSR: django.gettext('Enable this option to allow users who are not registered to participate in the voting process.'),
  hideResultsUntilFinishedLabel: django.gettext('Hide results until participation is over'),
  hideResultsUntilFinishedSR: django.gettext('Enable this option to hide the poll results from participants until the participation phase has ended.'),
  questionsTitle: django.gettext('Questions'),
  save: django.gettext('Save'),
  updated: django.gettext('The poll has been updated.'),
  updateFailed: django.gettext('The poll could not be updated. Please check the data you entered again.'),
  loadFailed: django.gettext('The poll could not be loaded. Please try again.')
}

const hasQuestionErrors = (errors: QuestionErrors | undefined): boolean =>
  Boolean(errors && Object.keys(errors).some((field) => {
    const value = (errors as Record<string, unknown>)[field]
    return Array.isArray(value) ? value.length > 0 : Boolean(value)
  }))

export const PollManagement = (props: PollManagementProps) => {
  const [questions, setQuestions] = useState<ManagementQuestion[]>([])
  const [allowUnregisteredUsers, setAllowUnregisteredUsers] = useState(false)
  const [hideResultsUntilFinished, setHideResultsUntilFinished] = useState(false)
  const [errors, setErrors] = useState<QuestionErrors[]>([])
  const [alert, setAlert] = useState<AlertValue | null>(null)
  const [expandedKey, setExpandedKey] = useState<string | null>(null)
  const [snapshot, setSnapshot] = useState<ManagementQuestion | null>(null)
  const [dragIndex, setDragIndex] = useState<number | null>(null)
  const [overIndex, setOverIndex] = useState<number | null>(null)

  useEffect(() => {
    api.poll.get(props.pollId).done((result: any) => {
      const initialQuestions = result.questions.length
        ? result.questions.map(normalizeQuestion)
        : [createEmptyQuestion(false)]
      setQuestions(initialQuestions)
      setAllowUnregisteredUsers(result.allow_unregistered_users)
      setHideResultsUntilFinished(result.hide_results_until_finished)
    }).fail(() => {
      setAlert({ type: 'danger', message: TRANSLATED.loadFailed })
    })
  }, [props.pollId])

  const expandedIndex = questions.findIndex((question) => question.key === expandedKey)

  const updateQuestion = (index: number, updates: Partial<ManagementQuestion>) => {
    setQuestions((prev) => prev.map((question, i) => (
      i === index ? { ...question, ...updates } : question
    )))
  }

  const updateChoice = (questionIndex: number, choiceIndex: number, updates: Partial<ManagementQuestion['choices'][number]>) => {
    setQuestions((prev) => prev.map((question, i) => {
      if (i !== questionIndex) return question
      return {
        ...question,
        choices: question.choices.map((choice, j) => (
          j === choiceIndex ? { ...choice, ...updates } : choice
        ))
      }
    }))
  }

  const clearAlert = () => {
    setAlert(null)
    setErrors([])
  }

  const handleEdit = (key: string) => {
    // clicking the row again collapses it, keeping the local edits
    if (key === expandedKey) {
      setExpandedKey(null)
      setSnapshot(null)
      return
    }
    const question = questions.find((item) => item.key === key)
    if (question) {
      setExpandedKey(key)
      setSnapshot(cloneQuestion(question))
    }
  }

  const handleItemSave = () => {
    setExpandedKey(null)
    setSnapshot(null)
  }

  const handleItemCancel = () => {
    if (snapshot && expandedIndex >= 0) {
      updateQuestion(expandedIndex, cloneQuestion(snapshot))
    }
    setExpandedKey(null)
    setSnapshot(null)
  }

  const handleNavigate = (direction: -1 | 1) => {
    const newIndex = expandedIndex + direction
    if (newIndex < 0 || newIndex >= questions.length) return
    setExpandedKey(questions[newIndex].key)
    setSnapshot(cloneQuestion(questions[newIndex]))
  }

  const handleQuestionAppend = (isOpen: boolean) => {
    const question = createEmptyQuestion(isOpen)
    setQuestions((prev) => [...prev, question])
    setExpandedKey(question.key)
    setSnapshot(cloneQuestion(question))
    setErrors([])
  }

  const handleQuestionDelete = (index: number) => {
    if (questions[index].key === expandedKey) {
      setExpandedKey(null)
      setSnapshot(null)
    }
    setQuestions((prev) => prev.filter((_, i) => i !== index))
    setErrors([])
  }

  const handleDragStart = (index: number) => setDragIndex(index)

  const handleDragEnter = (index: number) => {
    if (dragIndex !== null && index !== overIndex) {
      setOverIndex(index)
    }
  }

  const handleDrop = () => {
    if (dragIndex !== null && overIndex !== null) {
      setQuestions((prev) => moveItem(prev, dragIndex, overIndex))
      setErrors([])
    }
    handleDragEnd()
  }

  const handleDragEnd = () => {
    setDragIndex(null)
    setOverIndex(null)
  }

  const handleChoiceLabelChange = (choiceIndex: number, label: string) => {
    updateChoice(expandedIndex, choiceIndex, { label })
  }

  const handleChoiceDelete = (choiceIndex: number) => {
    setQuestions((prev) => prev.map((question, i) => {
      if (i !== expandedIndex) return question
      return {
        ...question,
        choices: question.choices.filter((_, j) => j !== choiceIndex)
      }
    }))
  }

  const handleChoiceAppend = () => {
    setQuestions((prev) => prev.map((question, i) => {
      if (i !== expandedIndex) return question
      const hasOtherOption = question.choices.some((choice) => choice.is_other_choice)
      const position = hasOtherOption ? question.choices.length - 1 : question.choices.length
      const choices = [...question.choices]
      choices.splice(position, 0, createEmptyChoice())
      return { ...question, choices }
    }))
  }

  const handleOtherChoiceToggle = () => {
    setQuestions((prev) => prev.map((question, i) => {
      if (i !== expandedIndex) return question
      const hasOtherOption = question.choices.some((choice) => choice.is_other_choice)
      if (hasOtherOption) {
        return {
          ...question,
          choices: question.choices.filter((choice) => !choice.is_other_choice)
        }
      }
      return { ...question, choices: [...question.choices, createEmptyChoice(true)] }
    }))
  }

  const handleImageChange = (base64: string) => {
    updateQuestion(expandedIndex, {
      image_base64: base64 || '',
      image_url: base64 || null,
      image_alt_text: ''
    })
  }

  const handleAltTextChange = (altText: string) => {
    updateQuestion(expandedIndex, { image_alt_text: altText })
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const payload = {
      questions: buildQuestionsPayload(questions),
      allow_unregistered_users: allowUnregisteredUsers,
      hide_results_until_finished: hideResultsUntilFinished
    }

    api.poll.change(payload, props.pollId)
      .done((response: any) => {
        setQuestions(response.questions.map((question: any) => ({
          ...normalizeQuestion(question),
          image_base64: null
        })))
        setErrors([])
        setExpandedKey(null)
        setSnapshot(null)
        setAlert({ type: 'success', message: TRANSLATED.updated })
        if (props.reloadOnSuccess) updateDashboard()
      })
      .fail((xhr: any) => {
        let questionErrors: QuestionErrors[] = []
        try {
          const parsed = xhr && xhr.responseText ? JSON.parse(xhr.responseText) : null
          if (parsed && Array.isArray(parsed.questions)) {
            questionErrors = parsed.questions
          }
        } catch {
          // response body was not valid JSON, fall back to the generic alert
        }
        setErrors(questionErrors)
        const firstErrorIndex = questionErrors.findIndex(hasQuestionErrors)
        if (firstErrorIndex !== -1 && questions[firstErrorIndex]) {
          setExpandedKey(questions[firstErrorIndex].key)
          setSnapshot(cloneQuestion(questions[firstErrorIndex]))
        }
        setAlert({ type: 'danger', message: TRANSLATED.updateFailed })
      })
  }

  return (
    <form className="poll-management" onSubmit={handleSubmit} onChange={clearAlert}>
      <section className="poll-management__options">
        <h2 className="poll-management__section-title">{TRANSLATED.optionsTitle}</h2>
        {props.enableUnregisteredUsers && (
          <div className="poll-management__option form-check">
            <input
              type="checkbox"
              id="allowUnregisteredUsersCheckbox"
              onChange={() => setAllowUnregisteredUsers((value) => !value)}
              checked={allowUnregisteredUsers}
              aria-describedby="votingDescription"
            />
            <label htmlFor="allowUnregisteredUsersCheckbox">
              {TRANSLATED.allowUnregisteredUsersLabel}
            </label>
            <p id="votingDescription" className="visually-hidden">
              {TRANSLATED.allowUnregisteredUsersSR}
            </p>
          </div>
        )}
        <div className="poll-management__option form-check">
          <input
            type="checkbox"
            id="hideResultsUntilFinishedCheckbox"
            onChange={() => setHideResultsUntilFinished((value) => !value)}
            checked={hideResultsUntilFinished}
            aria-describedby="hideResultsDescription"
          />
          <label htmlFor="hideResultsUntilFinishedCheckbox">
            {TRANSLATED.hideResultsUntilFinishedLabel}
          </label>
          <p id="hideResultsDescription" className="visually-hidden">
            {TRANSLATED.hideResultsUntilFinishedSR}
          </p>
        </div>
      </section>

      <section className="poll-management__questions">
        <h2 className="poll-management__section-title">{TRANSLATED.questionsTitle}</h2>

        <ul className="poll-management__list">
          {questions.map((question, index) => (
            <li key={question.key} className="poll-management__list-item">
              <QuestionListItem
                question={question}
                index={index}
                hasErrors={hasQuestionErrors(errors[index])}
                isExpanded={question.key === expandedKey}
                isDragging={dragIndex === index}
                isDragOver={overIndex === index && dragIndex !== null && dragIndex !== index}
                onEdit={() => handleEdit(question.key)}
                onDelete={() => handleQuestionDelete(index)}
                onDragStart={() => handleDragStart(index)}
                onDragEnter={() => handleDragEnter(index)}
                onDragEnd={handleDragEnd}
                onDrop={handleDrop}
              />
              {question.key === expandedKey && (
                <QuestionEditor
                  question={question}
                  index={index}
                  total={questions.length}
                  errors={errors[index] || {}}
                  questionImagesEnabled={Boolean(props.questionImagesEnabled)}
                  onLabelChange={(label) => updateQuestion(index, { label })}
                  onHelpTextChange={(helpText) => updateQuestion(index, { help_text: helpText })}
                  onConfidentialChange={(value) => updateQuestion(index, { is_confidential: value })}
                  onMultipleChoiceChange={(value) => updateQuestion(index, { multiple_choice: value })}
                  onImageChange={handleImageChange}
                  onAltTextChange={handleAltTextChange}
                  onChoiceLabelChange={handleChoiceLabelChange}
                  onChoiceDelete={handleChoiceDelete}
                  onChoiceAppend={handleChoiceAppend}
                  onOtherChoiceToggle={handleOtherChoiceToggle}
                  onNavigate={handleNavigate}
                  onSave={handleItemSave}
                  onCancel={handleItemCancel}
                />
              )}
            </li>
          ))}
        </ul>

        <Alert onClick={clearAlert} {...alert} />

        <div className="poll-management__footer">
          <AddQuestionDropdown
            onAddMultipleChoice={() => handleQuestionAppend(false)}
            onAddOpen={() => handleQuestionAppend(true)}
          />
          <button type="submit" className="btn btn--primary">
            {TRANSLATED.save}
          </button>
        </div>
      </section>
    </form>
  )
}
