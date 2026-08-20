import React from 'react'
import django from 'django'

interface ChapterNavItemProps {
  name: string
  index: number
  active?: boolean
  onClick?: () => void
  onMoveUp?: (() => void) | null
  onMoveDown?: (() => void) | null
  onDelete?: (() => void) | null
  errors?: Record<string, unknown> | null
}

function getErrorCount (props: ChapterNavItemProps) {
  if (props.errors && Object.keys(props.errors).length > 0) {
    let errorCount = Object.keys(props.errors).length
    if (props.errors.paragraphs) {
      errorCount = errorCount - 1 + Object.keys(props.errors.paragraphs as Record<string, unknown>).length
    }
    return <span className="text-danger"> ({errorCount})</span>
  }
  return null
}

const ChapterNavItem = (props: ChapterNavItemProps) => {
  return (
    <div className="commenting" data-testid="chapter-nav-item">
      <div className="commenting__content">
        <button
          type="button"
          className={(props.active && 'active') + ' commenting--toc__button btn btn--light btn--small'}
          onClick={props.onClick}
        >
          {props.index + 1}. {props.name}
          {getErrorCount(props)}
        </button>
      </div>

      <div className="commenting__actions btn--group" role="group">
        <button
          className="btn btn--light btn--small"
          onClick={props.onMoveUp ?? undefined}
          disabled={!props.onMoveUp}
          title={django.gettext('Move up')}
          type="button"
        >
          <i
            className="fa fa-chevron-up"
            aria-label={django.gettext('Move up')}
          />
        </button>
        <button
          className="btn btn--light btn--small"
          onClick={props.onMoveDown ?? undefined}
          disabled={!props.onMoveDown}
          title={django.gettext('Move down')}
          type="button"
        >
          <i
            className="fa fa-chevron-down"
            aria-label={django.gettext('Move down')}
          />
        </button>
        <button
          className="btn btn--light btn--small"
          onClick={props.onDelete ?? undefined}
          disabled={!props.onDelete}
          title={django.gettext('Delete')}
          type="button"
        >
          <i
            className="far fa-trash-alt"
            aria-label={django.gettext('Delete')}
          />
        </button>
      </div>
    </div>
  )
}

export default ChapterNavItem
