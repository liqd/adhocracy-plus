import React from 'react'
import django from 'django'

export default class QuestionUser extends React.Component {
  constructor (props) {
    super(props)

    this.state = {
      is_on_shortlist: this.props.is_on_shortlist,
      is_live: this.props.is_live,
      likes: this.props.likes.count,
      session_like: this.props.likes.session_like
    }
  }

  componentDidUpdate (prevProps) {
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

  handleErrors (response) {
    if (!response.ok) {
      throw Error(response.statusText)
    }
    return response
  }

  handleLike () {
    const value = !this.state.session_like
    this.props.handleLike(this.props.id, value)
      .then(this.handleErrors)
      .then((response) => this.setState(
        {
          session_like: value,
          likes: value ? this.state.likes + 1 : this.state.likes - 1
        }
      ))
      .catch((response) => { console.log(response.message) })
  }

  render () {
    const shortlistText = django.gettext('on shortlist')
    const likesText = django.gettext('likes')
    const ariaAddLike = django.gettext('add like')
    const ariaUndoLike = django.gettext('undo like')

    return (
      <div className="list-group-item border mb-2">
        <div>
          <p>
            {this.props.is_on_shortlist &&
              <i className="icon-in-list pr-1 text-muted" aria-label={shortlistText} />}
            {this.props.children}
          </p>
        </div>
        <div className="row">
          <div className="col-12">
            {this.props.category &&
              <span className="label label--big mr-1">{this.props.category}</span>}

            <div>
              {this.props.hasLikingPermission
                ? (
                  <button
                    type="button"
                    className={this.state.session_like ? 'rating-button rating-up float-right px-3' : 'rating-button rating-up is-selected float-right px-3'}
                    onClick={this.handleLike.bind(this)}
                    aria-label={this.state.session_like ? ariaAddLike : ariaUndoLike}
                    title={this.state.session_like ? ariaAddLike : ariaUndoLike}
                  >
                    <span>{this.state.likes} </span>
                    <span className="sr-only">{likesText}</span>
                    <i className="fa fa-chevron-up" aria-hidden="true" />
                  </button>
                  )
                : (
                  <div className="float-right">
                    <span className="text-muted">{this.state.likes}</span>
                    <span className="sr-only">{likesText}</span>
                    <i className="fa fa-chevron-up text-muted ml-1" aria-hidden="true" />
                  </div>
                  )}
            </div>
          </div>
        </div>
      </div>
    )
  }
}
