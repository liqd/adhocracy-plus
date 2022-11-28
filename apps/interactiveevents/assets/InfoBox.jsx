import React from 'react'
import django from 'django'

const textInfo = django.gettext('Info')
const textDisplayQuestion = django.gettext('display question on screen')
const textAddQuestion = django.gettext('add question to shortlist')
const textHideQuestion = django.gettext('hide question from audience')
const textMarkAnswered = django.gettext('mark question as answered')
const textMarkedModeration = django.gettext('is shown in front of a question? It has been marked by the moderation.')
const ariaCloseInfo = django.gettext('Close information')
const ariaOpenInfo = django.gettext('Open information')

export default class InfoBox extends React.Component {
  constructor (props) {
    super(props)

    this.state = {
      displayInfo: false
    }
  }

  toggleInformation () {
    const displayInfo = !this.state.displayInfo
    this.setState({
      displayInfo
    })
  }

  render () {
    return (
      <div className={this.state.displayInfo ? 'livequestion__info-box--open' : 'order-2'}>
        {this.state.displayInfo &&
          <div className="u-border my-2">
            <button type="button" className="livequestion__close" onClick={this.toggleInformation.bind(this)}>
              <span aria-label={ariaCloseInfo}>&times;</span>
            </button>
            {this.props.isModerator &&
              <div className="row">
                <div className="col-lg-3 text-center">
                  <i className="icon-push-in-list" /> <div>{textAddQuestion}</div>
                </div>
                <div className="col-lg-3 text-center">
                  <span className="fa-stack fa-1x"><i className="fas fa-tv fa-stack-2x" /><i className="fas fa-arrow-up fa-stack-1x" /></span> <div>{textDisplayQuestion}</div>
                </div>
                <div className="col-lg-3 text-center">
                  <i className="icon-answered" /> <div>{textMarkAnswered}</div>
                </div>
                <div className="col-lg-3 text-center pb-3">
                  <i className="far fa-eye" /> <div>{textHideQuestion}</div>
                </div>
              </div>}
            {!this.props.isModerator &&
              <div className="row">
                <div className="col-12 text-center mb-3">
                  <i className="icon-in-list" /> <div>{textMarkedModeration}</div>
                </div>
              </div>}
          </div>}
        {!this.state.displayInfo &&
          <button type="button" className="btn btn--none text-muted pe-0" onClick={this.toggleInformation.bind(this)}>
            <span aria-label={ariaOpenInfo}><i className="fas fa-info-circle me-1" />{textInfo}</span>
          </button>}
      </div>
    )
  }
}
