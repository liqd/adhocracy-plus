import React from 'react'
import django from 'django'
import type { LikeInfo } from './types'

interface QuestionUserProps {
  is_on_shortlist: boolean
  is_live: boolean
  likes: LikeInfo
  id: number
  children?: React.ReactNode
  category?: string
  hasLikingPermission?: boolean
  handleLike?: (id: number, value: boolean) => Promise<Response>
}

interface QuestionUserState {
  is_on_shortlist: boolean
  is_live: boolean
  likes: number
  session_like: boolean
}

export default class QuestionUser extends React.Component<QuestionUserProps, QuestionUserState> {
  constructor (props: QuestionUserProps) {
    super(props)

    this.state = {
      is_on_shortlist: this.props.is_on_shortlist,
      is_live: this.props.is_live,
      likes: this.props.likes.count,
      session_like: this.props.likes.session_like
    }
  }

  componentDidUpdate (prevProps: QuestionUserProps) {
    if (this.props.is_on_shortlist !== prevProps.is_on_shortlist) {
      this.setState({
        is_on_shortlist: this.props.is_on_shortlist
      })
    }
    if (this.props.likes !== prevProps.likes) {
      this.setState({
        likes: this.props.likes.count,
        session_like: this.props.likes.session_like
      })
    }
  }

  handleErrors (response: Response) {
    if (!response.ok) {
      throw Error(response.statusText)
    }
    return response
  }

  handleLike () {
    const value = !this.state.session_like
    const likePromise = this.props.handleLike?.(this.props.id, value)
    if (!likePromise) return
    likePromise
      .then(this.handleErrors)
      .then(() => this.setState(
        {
          session_like: value,
          likes: value ? this.state.likes + 1 : this.state.likes - 1
        }
      ))
      .catch((response: Error) => { console.log(response.message) })
  }

  render () {
    const shortlistText = django.gettext('on shortlist')
    const likesText = django.gettext('likes')
    const ariaAddLike = django.gettext('add like')
    const ariaUndoLike = django.gettext('undo like')

    return (
      <div className="list-item border mb-2 p-4">
        <div>
          <div className="col-12">
            {this.props.category &&
              <span className="badge mb-2">{this.props.category}</span>}

            <div>
              <p>
                {this.props.is_on_shortlist &&
                  <i className="icon-in-list pe-2 text-muted" aria-label={shortlistText} />}
                {this.props.children}
              </p>
            </div>
            <div>
              {this.props.hasLikingPermission
                ? (
                  <button
                    type="button"
                    className={'rating-button rating-up ' + (this.state.session_like ? 'is-selected' : '')}
                    onClick={this.handleLike.bind(this)}
                    aria-label={this.state.session_like ? ariaUndoLike : ariaAddLike}
                    title={this.state.session_like ? ariaUndoLike : ariaAddLike}
                  >
                    <span>{this.state.likes} </span>
                    <span className="visually-hidden">{likesText}</span>
                    <i className="fa fa-thumbs-up" aria-hidden="true" />
                  </button>
                  )
                : (
                  <div className="float-right">
                    <span className="text-muted">{this.state.likes}</span>
                    <span className="visually-hidden">{likesText}</span>
                    <i className="fa fa-thumbs-up text-muted ms-1" aria-hidden="true" />
                  </div>
                  )}
            </div>
          </div>
        </div>
      </div>
    )
  }
}
