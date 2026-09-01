// apps/polls/assets/react_poll_management/components/QuestionListItem.tsx
import React from 'react'
import django from 'django'

import type { ManagementQuestion } from '../types'

const TRANSLATED = {
  question: django.gettext('Question'),
  untitled: django.gettext('Untitled question'),
  multipleChoice: django.gettext('Multiple choice'),
  singleChoice: django.gettext('Single choice'),
  open: django.gettext('Open'),
  delete: django.gettext('Delete question'),
  expand: django.gettext('Expand question'),
  collapse: django.gettext('Collapse question')
}

const typeLabel = (question: ManagementQuestion): string => {
  if (question.is_open) {
    return TRANSLATED.open
  }
  return question.multiple_choice ? TRANSLATED.multipleChoice : TRANSLATED.singleChoice
}

interface QuestionListItemProps {
  question: ManagementQuestion
  index: number
  hasErrors: boolean
  isExpanded: boolean
  isDragging: boolean
  isDragOver: boolean
  onEdit: () => void
  onDelete: () => void
  onDragStart: () => void
  onDragEnter: () => void
  onDragEnd: () => void
  onDrop: () => void
}

export const QuestionListItem = ({
  question,
  index,
  hasErrors,
  isExpanded,
  isDragging,
  isDragOver,
  onEdit,
  onDelete,
  onDragStart,
  onDragEnter,
  onDragEnd,
  onDrop
}: QuestionListItemProps) => {
  const classNames = [
    'poll-management__item',
    isExpanded ? 'poll-management__item--active' : '',
    isDragging ? 'poll-management__item--dragging' : '',
    isDragOver ? 'poll-management__item--drag-over' : '',
    hasErrors ? 'poll-management__item--error' : ''
  ].filter(Boolean).join(' ')

  return (
    <div
      className={classNames}
      draggable
      onDragStart={(e) => {
        if (e.dataTransfer) {
          e.dataTransfer.effectAllowed = 'move'
          // Firefox only initiates a drag when data is explicitly set
          e.dataTransfer.setData('text/plain', String(index))
        }
        onDragStart()
      }}
      onDragEnter={onDragEnter}
      onDragOver={(e) => {
        e.preventDefault()
        if (e.dataTransfer) {
          e.dataTransfer.dropEffect = 'move'
        }
      }}
      onDrop={(e) => {
        e.preventDefault()
        e.stopPropagation()
        onDrop()
      }}
      onDragEnd={onDragEnd}
    >
      <span className="poll-management__drag-handle" aria-hidden="true">
        <i className="fa fa-grip-lines" />
      </span>

      {/* not a native button: Firefox does not start the parent drag from
          form controls, so the whole row doubles as the expand target */}
      <div
        className="poll-management__summary"
        role="button"
        tabIndex={0}
        aria-expanded={isExpanded}
        onClick={onEdit}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            onEdit()
          }
        }}
      >
        <span className="poll-management__number">
          {`${TRANSLATED.question} ${index + 1}`}
        </span>
        <span className={`poll-management__label ${question.label ? '' : 'poll-management__label--empty'}`}>
          {question.label || TRANSLATED.untitled}
        </span>
        <span className="poll-management__type">
          {typeLabel(question)}
        </span>
      </div>

      <button
        type="button"
        className="poll-management__collapse"
        onClick={onEdit}
        aria-label={isExpanded ? TRANSLATED.collapse : TRANSLATED.expand}
        title={isExpanded ? TRANSLATED.collapse : TRANSLATED.expand}
      >
        <i className={`fa ${isExpanded ? 'fa-chevron-up' : 'fa-chevron-down'}`} aria-hidden="true" />
      </button>

      <button
        type="button"
        className="poll-management__delete"
        aria-label={TRANSLATED.delete}
        title={TRANSLATED.delete}
        onClick={onDelete}
      >
        <i className="fas fa-trash-alt" aria-hidden="true" />
      </button>
    </div>
  )
}
