import React, { Component } from 'react'
import django from 'django'

export default class ModerationComment extends Component {
  render () {
    const { classification, commentText, commentUrl, created, userImage, userName, aiClassified } = this.props
    const postedText = django.pgettext('kosmo', ' posted a ')
    const offensiveTextReport = django.pgettext('kosmo', ' that has been reported as ')
    const offensiveTextAI = django.pgettext('kosmo', ' that might be ')
    const classificationText = django.pgettext('kosmo', 'Classification: ')
    const aiText = django.pgettext('kosmo', 'AI')
    const blockText = django.pgettext('kosmo', ' Block')
    const dismissText = django.pgettext('kosmo', ' Dismiss')
    const replyText = django.pgettext('kosmo', ' Reply')

    let userImageDiv
    if (userImage) {
      const sectionStyle = {
        backgroundImage: 'url(' + userImage + ')'
      }
      userImageDiv = <div className="user-avatar user-avatar--small user-avatar--shadow mb-1 userindicator__btn-img" style={sectionStyle} />
    }

    return (
      <div>
        <div className="row">
          <div className="col-2 col-md-1">
            {userImageDiv}
          </div>
          <div className="col-7 col-md-8">
            <div><span className="fa-stack fa-2x" aria-hidden="true"><i className="fas fa-exclamation fa-stack-1x" /><i className="far fa-circle fa-stack-2x" /></span>
              <a href="/">{userName}</a>
              <span className="text-lowercase">{postedText}<a href={commentUrl}>comment</a>{aiClassified ? offensiveTextAI : offensiveTextReport}{classification}</span>
            </div>
            <div>{created}</div>
          </div>
        </div>
        <div className="row">
          <div className="a4-comments__box--comment">
            <div className="col-12">
              <span className="sr-only">{classificationText}{classification}</span>
              <span className="badge a4-comments__badge a4-comments__badge--que">{classification}</span>
              {aiClassified && <span className="badge a4-comments__badge a4-comments__badge--que">{aiText}</span>}
            </div>
          </div>
        </div>
        <div className="row">
          <div className="col-12">
            <p>{commentText}</p>
          </div>
        </div>
        <div className="text-muted mt-3 d-flex justify-content-between">
          <div><i className="fas fa-reply" aria-hidden="true" />{replyText}</div>
          <div><i className="far fa-times-circle" aria-hidden="true" />{dismissText}</div>
          <div><i className="fas fa-ban" aria-hidden="true" />{blockText}</div>
        </div>
      </div>
    )
  }
}
