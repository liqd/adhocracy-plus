import React from 'react'
import FlipMove from 'react-flip-move'
import django from 'django'
import ChapterNavItem from './ChapterNavItem'
import type { Chapter, DocumentErrors } from './types'

interface ChapterNavProps {
  chapters: Chapter[]
  activeChapter: Chapter
  onMoveUp: (index: number) => void
  onMoveDown: (index: number) => void
  onDelete: (index: number) => void
  onChapterAppend: () => void
  onClick: (index: number) => void
  errors?: DocumentErrors | null
}

const ChapterNav = (props: ChapterNavProps) => {
  const activeKey = props.activeChapter.id || props.activeChapter.key
  return (
    <nav aria-label={django.gettext('Chapter navigation')}>
      <FlipMove easing="cubic-bezier(0.25, 0.5, 0.75, 1)" typeName="ol" className="u-list-reset">
        {
          props.chapters.map((chapter, index, arr) => {
            const key = chapter.id || chapter.key
            return (
              <li key={key}>
                <ChapterNavItem
                  name={chapter.name}
                  index={index}
                  onMoveUp={index !== 0 ? () => { props.onMoveUp(index) } : null}
                  onMoveDown={index < arr.length - 1 ? () => { props.onMoveDown(index) } : null}
                  onDelete={arr.length > 1 ? () => { props.onDelete(index) } : null}
                  onClick={() => { props.onClick(index) }}
                  errors={props.errors ? props.errors[index] : null}
                  active={key === activeKey}
                />
              </li>
            )
          })
        }
      </FlipMove>

      <p>
        <button
          className="btn btn--light btn--small"
          onClick={props.onChapterAppend}
          type="button"
        >
          <i className="fa fa-plus" /> {django.gettext('Add a new chapter')}
        </button>
      </p>
    </nav>
  )
}

export default ChapterNav
