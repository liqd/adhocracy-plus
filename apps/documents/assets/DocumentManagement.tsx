import React from 'react'
import { alert as Alert } from 'adhocracy4'
import api from 'adhocracy4/adhocracy4/static/api'
import django from 'django'
import dashboard from 'adhocracy4/adhocracy4/dashboard/assets/dashboard'
import update from 'immutability-helper'
import ChapterNav from './ChapterNav'
import ChapterForm from './ChapterForm'
import type { Chapter, ChapterParagraph, DocumentErrors } from './types'

interface DocumentAlert {
  type: string
  message: string
}

interface DocumentManagementProps {
  chapters?: Chapter[]
  module: number
  reloadOnSuccess?: boolean
  csrfCookieName?: string
  uploadUrl?: string
  uploadFileTypes?: string[]
  config?: Record<string, unknown>
}

interface DocumentManagementState {
  chapters: Chapter[]
  errors: DocumentErrors | null
  alert: DocumentAlert | null
  editChapterIndex: number
}

class DocumentManagement extends React.Component<DocumentManagementProps, DocumentManagementState> {
  maxLocalKey = 0

  constructor (props: DocumentManagementProps) {
    super(props)

    let chapters = this.props.chapters
    if (!chapters || chapters.length === 0) {
      chapters = [
        this.getNewChapter(django.gettext('first chapter'))
      ]
    }

    this.state = {
      chapters,
      errors: null,
      alert: null,
      editChapterIndex: 0
    }
  }

  getNextLocalKey () {
    /** Get an artificial key for non-committed items.
     *
     *  The key is prefixed to prevent collisions with real database keys.
     */
    this.maxLocalKey++
    return 'local_' + this.maxLocalKey
  }

  getNewChapter (name: string): Chapter {
    return {
      name,
      key: this.getNextLocalKey(),
      paragraphs: []
    }
  }

  handleChapterMoveUp (index: number) {
    const value = this.state.chapters[index]
    const diff = { $splice: [[index, 1], [index - 1, 0, value]] } as any
    let editChapterIndex = this.state.editChapterIndex
    if (index === editChapterIndex) {
      editChapterIndex--
    } else if (index - 1 === editChapterIndex) {
      editChapterIndex++
    }
    this.setState({
      chapters: update(this.state.chapters, diff),
      editChapterIndex
    })
  }

  handleChapterMoveDown (index: number) {
    const value = this.state.chapters[index]
    const diff = { $splice: [[index, 1], [index + 1, 0, value]] } as any
    let editChapterIndex = this.state.editChapterIndex
    if (index === editChapterIndex) {
      editChapterIndex++
    } else if (index + 1 === editChapterIndex) {
      editChapterIndex--
    }
    this.setState({
      chapters: update(this.state.chapters, diff),
      editChapterIndex
    })
  }

  handleChapterDelete (index: number) {
    const diff = { $splice: [[index, 1]] } as any
    let editChapterIndex = this.state.editChapterIndex
    if (index < editChapterIndex) {
      editChapterIndex--
    } else if (index === editChapterIndex) {
      editChapterIndex = 0
    }
    this.setState({
      chapters: update(this.state.chapters, diff),
      editChapterIndex
    })
  }

  handleChapterAppend () {
    const newChapter = this.getNewChapter(django.gettext('new chapter'))
    const newChapterIndex = this.state.chapters.length

    const diff = { $push: [newChapter] } as any
    this.setState({
      chapters: update(this.state.chapters, diff),
      editChapterIndex: newChapterIndex
    }, () => { this.focusOnChapter(newChapter) })
  }

  handleChapterNameChange (index: number, name: string) {
    const diff: any = {}
    diff[index] = {
      $merge: {
        name
      }
    }
    this.setState({
      chapters: update(this.state.chapters, diff)
    })
  }

  handleChapterEdit (index: number) {
    const chapter = this.state.chapters[index]
    this.setState({
      editChapterIndex: index
    }, () => { this.focusOnChapter(chapter) })
  }

  focusOnChapter (chapter: Chapter) {
    const key = chapter.id || chapter.key
    const id = 'id_chapters-' + key + '-name'
    window.document.getElementById(id)?.focus()
  }

  getNewParagraph (name = '', text = ''): ChapterParagraph {
    return {
      name,
      text,
      key: this.getNextLocalKey()
    }
  }

  handleParagraphAppend (chapterIndex: number) {
    const newParagraph = this.getNewParagraph()

    const diff: any = {}
    diff[chapterIndex] = {
      paragraphs: {
        $push: [newParagraph]
      }
    }

    this.setState({
      chapters: update(this.state.chapters, diff)
    }, () => { this.focusOnParagraph(newParagraph) })
  }

  handleParagraphMoveUp (chapterIndex: number, paragraphIndex: number) {
    const value = this.state.chapters[chapterIndex].paragraphs[paragraphIndex]
    const diff: any = {}
    diff[chapterIndex] = {
      paragraphs: {
        $splice: [[paragraphIndex, 1], [paragraphIndex - 1, 0, value]]
      }
    }
    this.setState({
      chapters: update(this.state.chapters, diff)
    })
  }

  handleParagraphMoveDown (chapterIndex: number, paragraphIndex: number) {
    const value = this.state.chapters[chapterIndex].paragraphs[paragraphIndex]
    const diff: any = {}
    diff[chapterIndex] = {
      paragraphs: {
        $splice: [[paragraphIndex, 1], [paragraphIndex + 1, 0, value]]
      }
    }
    this.setState({
      chapters: update(this.state.chapters, diff)
    })
  }

  handleParagraphDelete (chapterIndex: number, paragraphIndex: number) {
    const diff: any = {}
    diff[chapterIndex] = {
      paragraphs: {
        $splice: [[paragraphIndex, 1]]
      }
    }
    this.setState({
      chapters: update(this.state.chapters, diff)
    })
  }

  handleParagraphNameChange (chapterIndex: number, paragraphIndex: number, name: string) {
    const diff: any = {}
    diff[chapterIndex] = { paragraphs: [] }
    diff[chapterIndex].paragraphs[paragraphIndex] = {
      $merge: {
        name
      }
    }
    this.setState({
      chapters: update(this.state.chapters, diff)
    })
  }

  handleParagraphTextChange (chapterIndex: number, paragraphIndex: number, text: string) {
    const diff: any = {}
    diff[chapterIndex] = { paragraphs: [] }
    diff[chapterIndex].paragraphs[paragraphIndex] = {
      $merge: {
        text
      }
    }
    this.setState({
      chapters: update(this.state.chapters, diff),
      // Workaround missing change events when using CKEDITOR
      alert: null
    })
  }

  focusOnParagraph (paragraph: ChapterParagraph) {
    const key = paragraph.id || paragraph.key
    const id = 'id_paragraphs-' + key + '-name'
    window.document.getElementById(id)?.focus()
  }

  removeAlert () {
    this.setState({
      alert: null
    })
  }

  handleSubmit (e: React.FormEvent) {
    if (e) {
      e.preventDefault()
    }

    const submitData = {
      urlReplaces: { moduleId: this.props.module },
      chapters: this.state.chapters
    }

    api.document.add(submitData)
      .done((data: any) => {
        this.setState({
          alert: {
            type: 'success',
            message: django.gettext('The document has been updated.')
          },
          errors: null,
          chapters: data.chapters
        })
        if (this.props.reloadOnSuccess) {
          dashboard.updateDashboard()
        }
      })
      .fail((xhr: any) => {
        let errors: DocumentErrors | null = null
        if (xhr.responseJSON && 'chapters' in xhr.responseJSON) {
          errors = xhr.responseJSON.chapters
        }

        this.setState({
          alert: {
            type: 'danger',
            message: django.gettext('The document could not be updated.')
          },
          errors
        })
      })
  }

  render () {
    const chapterIndex = this.state.editChapterIndex
    const chapterErrors = this.state.errors && this.state.errors[chapterIndex] ? this.state.errors[chapterIndex] as unknown as Record<string, unknown> : null
    const chapter = this.state.chapters[chapterIndex]
    const key = chapter.id || chapter.key

    return (
      <form onSubmit={this.handleSubmit.bind(this)} onChange={this.removeAlert.bind(this)}>

        <h2>{django.gettext('Contents')}</h2>
        <ChapterNav
          chapters={this.state.chapters}
          activeChapter={this.state.chapters[chapterIndex]}
          onMoveUp={this.handleChapterMoveUp.bind(this)}
          onMoveDown={this.handleChapterMoveDown.bind(this)}
          onDelete={this.handleChapterDelete.bind(this)}
          onChapterAppend={this.handleChapterAppend.bind(this)}
          onClick={this.handleChapterEdit.bind(this)}
          errors={this.state.errors}
        />

        <h2>{django.gettext('Edit chapter')}</h2>
        <ChapterForm
          id={String(key)}
          onChapterNameChange={(name) => { this.handleChapterNameChange(chapterIndex, name) }}
          onParagraphNameChange={(paragraphIndex, name) => { this.handleParagraphNameChange(chapterIndex, paragraphIndex, name) }}
          onParagraphTextChange={(paragraphIndex, text) => { this.handleParagraphTextChange(chapterIndex, paragraphIndex, text) }}
          onParagraphAppend={() => { this.handleParagraphAppend(chapterIndex) }}
          onParagraphMoveUp={(paragraphIndex) => { this.handleParagraphMoveUp(chapterIndex, paragraphIndex) }}
          onParagraphMoveDown={(paragraphIndex) => { this.handleParagraphMoveDown(chapterIndex, paragraphIndex) }}
          onParagraphDelete={(paragraphIndex) => { this.handleParagraphDelete(chapterIndex, paragraphIndex) }}
          csrfCookieName={this.props.csrfCookieName}
          uploadUrl={this.props.uploadUrl}
          uploadFileTypes={this.props.uploadFileTypes}
          config={this.props.config}
          chapter={chapter}
          errors={chapterErrors}
        />

        <Alert onClick={this.removeAlert.bind(this)} {...this.state.alert} />
        <div className="d-flex justify-content-end">
          <button type="submit" className="btn btn--primary">{django.gettext('Save')}</button>
        </div>
      </form>
    )
  }
}

export default DocumentManagement
