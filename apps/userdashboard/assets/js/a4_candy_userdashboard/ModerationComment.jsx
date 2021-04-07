import React, { Component } from 'react'
import django from 'django'

export default class ModerationComment extends Component {
  constructor (props) {
    super(props)

    this.state = {
      project: this.props.key
    }
  }

  render () {
    const postedText = django.gettext(' posted a ')
    const offensiveText = django.gettext(' for being offensive')
    const categoryText = django.gettext('Categories: ')
    const blockText = django.gettext(' Block')
    const dismissText = django.gettext(' Dismiss')
    const replyText = django.gettext(' Reply')

    return (
      <div className="mt-5">
        <ul className="pl-0">
          <li className="list-item ">
            <div className="row">
              <div className="col-2 col-md-1">
                <div className="user-avatar user-avatar--small user-avatar--shadow mb-1 userindicator__btn-img" />
              </div>
              <div className="col-7 col-md-8">
                <div><span className="fa-stack fa-2x" aria-hidden="true"><i className="fas fa-exclamation fa-stack-1x" /><i className="far fa-circle fa-stack-2x" /></span>
                  <a href="/">Profile name</a>
                  <span>{postedText}<a href="/">comment link</a>{offensiveText}</span>
                </div>
                <div>8.4.2021, 14:09</div>
              </div>
            </div>
            <div className="row">
              <div className="a4-comments__box--comment">
                <div className="col-12">
                  <span className="sr-only">{categoryText}</span>
                  <span className="badge a4-comments__badge a4-comments__badge--que">Category</span>
                </div>
              </div>
            </div>
            <div className="row">
              <div className="col-12">
                <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliter homines, aliter philosophos loqui putas oportere? Igitur neque stultorum quisquam beatus neque sapientium non beatus.</p>
              </div>
            </div>
            <div className="text-muted mt-3 d-flex justify-content-between">
              <div><i className="fas fa-reply" aria-hidden="true" />{replyText}</div>
              <div><i className="far fa-times-circle" aria-hidden="true" />{dismissText}</div>
              <div><i className="fas fa-ban" aria-hidden="true" />{blockText}</div>
            </div>
          </li>
        </ul>
      </div>
    )
  }
}
