// apps/polls/assets/react_poll_management/components/PollManagement.tsx
import React, { useEffect, useRef, useState } from 'react'
import django from 'django'

import api from 'adhocracy4/adhocracy4/static/api'
import { alert as Alert } from 'adhocracy4'
import { updateDashboard } from 'adhocracy4/adhocracy4/dashboard/assets/dashboard'

import { AddQuestionDropdown } from './AddQuestionDropdown'
import { QuestionEditor } from './QuestionEditor'
import { QuestionListItem } from './QuestionListItem'
import {
  buildQuestionsPayload,
  createEmptyChoice,
  createEmptyQuestion,
  moveItem,
  normalizeQuestion
} from '../utils'
import type {
  AlertValue,
  ChoiceErrors,
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
  addQuestion: django.gettext('New question'),
  save: django.gettext('Save'),
  updated: django.gettext('The poll has been updated.'),
  updateFailed: django.gettext('The poll could not be updated. Please check the data you entered again.'),
  unsavedChanges: django.gettext('If you leave this page changes you made will not be saved.'),
  loadFailed: django.gettext('The poll could not be loaded. Please try again.')
}

const hasQuestionErrors = (errors: QuestionErrors | undefined): boolean => {
  if (!errors) return false
  return Object.entries(errors).some(([field, value]) => {
    if (field === 'choices') {
      return Array.isArray(value) && value.some((choice) => (
        choice && Object.values(choice).some((entry) => (
          Array.isArray(entry) ? entry.length > 0 : Boolean(entry)
        ))
      ))
    }
    return Array.isArray(value) ? value.length > 0 : Boolean(value)
  })
}

const collectErrorMessages = (questionErrors: QuestionErrors[]): string[] => {
  const messages: string[] = []
  questionErrors.forEach((questionError) => {
    if (!questionError) return
    Object.values(questionError).forEach((value) => {
      if (!value) return
      if (Array.isArray(value)) {
        value.forEach((entry) => {
          if (typeof entry === 'string' && entry) {
            messages.push(entry)
          } else if (entry && typeof entry === 'object') {
            Object.values(entry).forEach((nested) => {
              if (Array.isArray(nested) && nested[0]) {
                messages.push(String(nested[0]))
              }
            })
          }
        })
      } else if (typeof value === 'string') {
        messages.push(value)
      }
    })
  })
  return messages.filter((message, index) => messages.indexOf(message) === index)
}

export const PollManagement = (props: PollManagementProps) => {
  const [questions, setQuestions] = useState<ManagementQuestion[]>([])
  const [allowUnregisteredUsers, setAllowUnregisteredUsers] = useState(false)
  const [hideResultsUntilFinished, setHideResultsUntilFinished] = useState(false)
  const [errors, setErrors] = useState<QuestionErrors[]>([])
  const [alert, setAlert] = useState<AlertValue | null>(null)
  const [expandedKey, setExpandedKey] = useState<string | null>(null)
  const [dragIndex, setDragIndex] = useState<number | null>(null)
  const [overIndex, setOverIndex] = useState<number | null>(null)
  const [dirty, setDirty] = useState(false)
  const focusErrorRef = useRef(false)
  const scrollToEditorRef = useRef(false)

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

  // Native unsaved-changes warning. The global unload_warning.js only arms on
  // native "change" events, so button-only edits (answer type, add/delete,
  // reorder) would not be covered. Track a dirty flag for every edit.
  useEffect(() => {
    if (!dirty) return undefined
    const handler = (event: BeforeUnloadEvent) => {
      event.preventDefault()
      event.returnValue = TRANSLATED.unsavedChanges
      return TRANSLATED.unsavedChanges
    }
    window.addEventListener('beforeunload', handler)
    return () => window.removeEventListener('beforeunload', handler)
  }, [dirty])

  // Move focus (and the viewport) to the first invalid field after a failed save.
  useEffect(() => {
    if (!focusErrorRef.current || !expandedKey) return
    const field = document.querySelector<HTMLElement>('.poll-management__editor [aria-invalid="true"]')
    if (field) {
      field.focus()
      field.scrollIntoView?.({ block: 'center' })
    }
    focusErrorRef.current = false
  }, [errors, expandedKey, questions])

  // Keep the edited question in view after a successful save.
  useEffect(() => {
    if (!scrollToEditorRef.current || !expandedKey) return
    const editor = document.querySelector<HTMLElement>('.poll-management__editor')
    editor?.scrollIntoView?.({ block: 'start', behavior: 'smooth' })
    scrollToEditorRef.current = false
  }, [expandedKey, questions])

  const markDirty = () => setDirty(true)

  const updateQuestion = (index: number, updates: Partial<ManagementQuestion>) => {
    setQuestions((prev) => prev.map((question, i) => (
      i === index ? { ...question, ...updates } : question
    )))
    markDirty()
    // Only clear the errors of the fields that were actually edited, so the
    // remaining invalid fields stay marked until they are fixed as well.
    setErrors((prev) => {
      const questionError = prev[index]
      if (!questionError) return prev
      const fields = Object.keys(updates)
      if (!fields.some((field) => field in questionError)) return prev
      const next = [...prev]
      const cleared = { ...questionError }
      fields.forEach((field) => { delete cleared[field] })
      next[index] = cleared
      return next
    })
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
    markDirty()
    setErrors((prev) => {
      const questionError = prev[questionIndex]
      const choiceErrors = questionError?.choices
      if (!questionError || !Array.isArray(choiceErrors)) return prev
      const current = choiceErrors[choiceIndex]
      if (!current) return prev
      const fields = Object.keys(updates)
      if (!fields.some((field) => field in current)) return prev
      const next = [...prev]
      const nextChoices = [...choiceErrors]
      const cleared: Record<string, unknown> = { ...current }
      fields.forEach((field) => { delete cleared[field] })
      nextChoices[choiceIndex] = cleared as ChoiceErrors
      next[questionIndex] = { ...questionError, choices: nextChoices }
      return next
    })
  }

  const clearAlert = () => {
    setAlert(null)
  }

  const handleEdit = (key: string) => {
    // clicking the row again collapses it, keeping the local edits
    if (key === expandedKey) {
      setExpandedKey(null)
      return
    }
    if (questions.some((item) => item.key === key)) {
      setExpandedKey(key)
    }
  }

  // The up/down controls change the position of the current question within
  // the survey instead of navigating to a different question.
  const handleMove = (direction: -1 | 1) => {
    const newIndex = expandedIndex + direction
    if (expandedIndex < 0 || newIndex < 0 || newIndex >= questions.length) return
    setQuestions((prev) => moveItem(prev, expandedIndex, newIndex))
    markDirty()
    setErrors([])
  }

  const handleQuestionAppend = (isOpen: boolean, multipleChoice = false) => {
    const question = createEmptyQuestion(isOpen, multipleChoice)
    setQuestions((prev) => [...prev, question])
    setExpandedKey(question.key)
    markDirty()
    setErrors([])
  }

  const handleQuestionDelete = (index: number) => {
    if (questions[index].key === expandedKey) {
      setExpandedKey(null)
    }
    setQuestions((prev) => prev.filter((_, i) => i !== index))
    markDirty()
    setErrors([])
  }

  // Switching a question to/from the open (free text) type also adjusts the
  // choices: open questions have none, choice questions need at least two.
  const handleOpenChange = (isOpen: boolean) => {
    setQuestions((prev) => prev.map((question, i) => {
      if (i !== expandedIndex || question.is_open === isOpen) return question
      if (isOpen) {
        return { ...question, is_open: true, choices: [] }
      }
      return {
        ...question,
        is_open: false,
        choices: question.choices.length
          ? question.choices
          : [createEmptyChoice(), createEmptyChoice()]
      }
    }))
    markDirty()
  }

  // Single choice questions only keep one answer option, so switching to
  // single choice trims the extra regular choices (the "other" choice stays).
  const handleAnswerTypeChange = (multipleChoice: boolean) => {
    setQuestions((prev) => prev.map((question, i) => {
      if (i !== expandedIndex) return question
      if (multipleChoice || question.is_open) {
        return { ...question, multiple_choice: multipleChoice }
      }
      const otherChoice = question.choices.find((choice) => choice.is_other_choice)
      const firstRegular = question.choices.find((choice) => !choice.is_other_choice)
      const choices = firstRegular
        ? [firstRegular, ...(otherChoice ? [otherChoice] : [])]
        : question.choices
      return { ...question, multiple_choice: false, choices }
    }))
    markDirty()
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
      markDirty()
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
    markDirty()
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
    markDirty()
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
    markDirty()
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
    const submitExpandedIndex = expandedIndex

    api.poll.change(payload, props.pollId)
      .done((response: any) => {
        const normalized: ManagementQuestion[] = response.questions.map((question: any) => ({
          ...normalizeQuestion(question),
          image_base64: null
        }))
        setQuestions(normalized)
        setErrors([])
        // Keep the question that was being edited open and bring it back into
        // view instead of collapsing everything and jumping to the top.
        const savedQuestion = submitExpandedIndex >= 0 ? normalized[submitExpandedIndex] : undefined
        if (savedQuestion) {
          setExpandedKey(savedQuestion.key)
          scrollToEditorRef.current = true
        } else {
          setExpandedKey(null)
        }
        setDirty(false)
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
          focusErrorRef.current = true
        }
        const messages = collectErrorMessages(questionErrors)
        setAlert({
          type: 'danger',
          message: messages.length ? messages.join(' ') : TRANSLATED.updateFailed
        })
      })
  }

  return (
    <form className="poll-management" onSubmit={handleSubmit}>
      <section className="poll-management__questions">
        <div className="poll-management__questions-header">
          <h2 className="poll-management__section-title">{TRANSLATED.questionsTitle}</h2>
          <AddQuestionDropdown
            onAddMultipleChoice={() => handleQuestionAppend(false, true)}
            onAddOpen={() => handleQuestionAppend(true)}
          />
        </div>

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
                  onMultipleChoiceChange={handleAnswerTypeChange}
                  onOpenChange={handleOpenChange}
                  onImageChange={handleImageChange}
                  onAltTextChange={handleAltTextChange}
                  onChoiceLabelChange={handleChoiceLabelChange}
                  onChoiceDelete={handleChoiceDelete}
                  onChoiceAppend={handleChoiceAppend}
                  onOtherChoiceToggle={handleOtherChoiceToggle}
                  onMove={handleMove}
                />
              )}
            </li>
          ))}
        </ul>

        <Alert onClick={clearAlert} {...alert} />

        <div className="poll-management__footer">
          <AddQuestionDropdown
            onAddMultipleChoice={() => handleQuestionAppend(false, true)}
            onAddOpen={() => handleQuestionAppend(true)}
          />
          <button type="submit" className="btn btn--primary">
            {TRANSLATED.save}
          </button>
        </div>

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
      </section>
    </form>
  )
}
