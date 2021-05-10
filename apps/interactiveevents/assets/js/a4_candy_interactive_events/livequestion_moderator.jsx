import React from 'react'
import django from 'django'

export default class QuestionModerator extends React.Component {
  constructor (props) {
    super(props)

    this.state = {
      is_on_shortlist: this.props.is_on_shortlist,
      is_live: this.props.is_live,
      likes: this.props.likes.count,
      session_like: this.props.likes.session_like,
      is_hidden: this.props.is_hidden,
      is_answered: this.props.is_answered
    }
  }

  toggleIsOnShortList () {
    const value = !this.state.is_on_shortlist
    const boolValue = (value) ? 1 : 0
    const data = { is_on_shortlist: boolValue }
    this.props.updateQuestion(data, this.props.id)
      .then((response) => response.json())
      .then(responseData => this.setState(
        {
          is_on_shortlist: responseData.is_on_shortlist
        }
      ))
      .then(() => this.props.togglePollingPaused())
  }

  toggleIslive () {
    const value = !this.state.is_live
    const boolValue = (value) ? 1 : 0
    const data = { is_live: boolValue }
    this.props.updateQuestion(data, this.props.id)
      .then((response) => response.json())
      .then(responseData => this.setState(
        {
          is_live: responseData.is_live
        }
      ))
      .then(() => this.props.togglePollingPaused())
  }

  toggleIsAnswered () {
    const value = !this.state.is_answered
    const boolValue = (value) ? 1 : 0
    const data = { is_answered: boolValue }
    this.props.removeFromList(this.props.id, data)
  }

  toggleIshidden () {
    const value = !this.state.is_hidden
    const boolValue = (value) ? 1 : 0
    const data = { is_hidden: boolValue }
    this.props.updateQuestion(data, this.props.id)
      .then((response) => response.json())
      .then(responseData => this.setState(
        {
          is_hidden: responseData.is_hidden
        }
      ))
      .then(() => this.props.togglePollingPaused())
  }

  componentDidUpdate (prevProps) {
    if (this.props.is_on_shortlist !== prevProps.is_on_shortlist) {
      this.setState({
        is_on_shortlist: this.props.is_on_shortlist
      })
    }
    if (this.props.is_live !== prevProps.is_live) {
      this.setState({
        is_live: this.props.is_live
      })
    }
    if (this.props.is_hidden !== prevProps.is_hidden) {
      this.setState({
        is_hidden: this.props.is_hidden
      })
    }
    if (this.props.is_answered !== prevProps.is_answered) {
      this.setState({
        is_answered: this.props.is_answered
      })
    }
    if (this.props.likes !== prevProps.likes) {
      this.setState({
        likes: this.props.likes.count,
        session_like: this.props.likes.session_like
      })
    }
  }

  render () {
    const ariaHidden = django.gettext('mark as hidden')
    const ariaUndoHidden = django.gettext('undo mark as hidden')
    const ariaMarkDone = django.gettext('mark as done')
    const ariaDisplayOnScreen = django.gettext('add to live list')
    const ariaRemoveDisplayScreen = django.gettext('remove from live list')
    const ariaAddShortlist = django.gettext('add to shortlist')
    const ariaRemoveShortlist = django.gettext('remove from shortlist')

    return (
      <div className="list-group-item border border-bottom rounded-0 mb-2">
        {this.props.category &&
          <span className="label mb-2">{this.props.category}</span>}
        <div>
          <p className={'text-break ' + (this.props.is_hidden ? 'text-muted u-text-line-through' : '')}>{this.props.children}</p>
        </div>
        <div className="row justify-content-between">
          <div className="col-12 col-md-4 col-sm-5 mb-3 mb-sm-0">
            <div className="mt-2 text-primary">{this.state.likes}<i className="fa fa-chevron-up ml-2" /></div>
          </div>
          <div className="col-12 col-md-8 col-sm-7">
            {this.props.displayIsHidden &&
              <button
                type="button" className="btn btn--transparent border-0 float-sm-right px-3"
                onClick={this.toggleIshidden.bind(this)}
                aria-label={this.props.is_hidden ? ariaUndoHidden : ariaHidden}
                title={this.props.is_hidden ? ariaUndoHidden : ariaHidden}
              >
                <i className={this.props.is_hidden ? 'far fa-eye-slash text-primary' : 'far fa-eye text-muted'} aria-hidden="true" />
              </button>}

            {this.props.displayIsAnswered &&
              <button
                type="button"
                className="btn btn--transparent border-0 float-sm-right px-3"
                onClick={this.toggleIsAnswered.bind(this)}
                aria-label={ariaMarkDone}
                title={ariaMarkDone}
              >
                <i
                  className={this.props.is_answered ? 'icon-answered px-1 text-primary' : 'icon-answered  text-muted px-1'}
                  aria-hidden="true"
                />
              </button>}
            {this.props.displayIsLive &&
              <button
                type="button"
                className="btn btn--transparent border-0 float-sm-right px-3"
                onClick={this.toggleIslive.bind(this)}
                aria-label={this.state.is_live ? ariaRemoveDisplayScreen : ariaDisplayOnScreen}
                title={this.state.is_live ? ariaRemoveDisplayScreen : ariaDisplayOnScreen}
              >
                <span className="fa-stack fa-1x">
                  <i className={this.state.is_live ? 'fas fa-tv fa-stack-2x text-primary' : 'fas fa-tv fa-stack-2x  text-muted'} aria-hidden="true" />
                  <i className={this.state.is_live ? 'fas fa-arrow-up fa-stack-1x fa-inverse text-primary' : 'fas fa-arrow-up fa-stack-1x text-muted'} aria-hidden="true" />
                </span>
              </button>}
            {this.props.displayIsOnShortlist &&
              <button
                type="button"
                className="btn btn--transparent border-0 float-sm-right px-3"
                onClick={this.toggleIsOnShortList.bind(this)}
                aria-label={this.state.is_on_shortlist ? ariaRemoveShortlist : ariaAddShortlist}
                title={this.state.is_on_shortlist ? ariaRemoveShortlist : ariaAddShortlist}
              >
                <i className={this.state.is_on_shortlist ? 'icon-in-list text-primary' : 'icon-push-in-list text-muted'} aria-hidden="true" />
              </button>}
          </div>
        </div>
      </div>
    )
  }
}
