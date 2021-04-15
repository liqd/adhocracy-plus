/* global fetch */
import React, { Component } from 'react'
import django from 'django'

export default class ModerationProjects extends Component {
  constructor (props) {
    super(props)

    this.state = {
      items: [],
      isLoaded: false
    }
  }

  componentDidMount () {
    this.loadData()
    this.timer = setInterval(() => this.loadData(), 3000)
  }

  async loadData () {
    fetch(this.props.projectApiUrl)
      .then(res => res.json())
      .then(json => {
        this.setState({
          items: json,
          isLoaded: true
        })
      }).catch((err) => {
        console.log(err)
      })
  }

  componentWillUnmount () {
    clearInterval(this.timer)
    this.timer = null
  }

  getTimespan (item) {
    const timeRemaining = item.active_phase[1].split(' ')
    const daysRemaining = parseInt(timeRemaining[0])
    if (daysRemaining > 365) {
      return (
        <span>{django.gettext('Over 1 year left')}</span>
      )
    } else {
      return (
        <span>{django.gettext('left')} {item.active_phase[1]}</span>
      )
    }
  }

  getMobileTimespan (item) {
    const timeRemaining = item.active_phase[1].split(' ')
    const daysRemaining = parseInt(timeRemaining[0])
    if (daysRemaining > 365) {
      return (
        <span>{django.gettext('1 year')}</span>
      )
    } else {
      return (
        <span>{item.active_phase[1]}</span>
      )
    }
  }

  render () {
    const { isLoaded, items } = this.state
    const loadingText = django.gettext('Loading...')
    const byText = django.gettext('By ')
    const commentCountText = django.gettext(' comments')
    const reportCountText = django.gettext(' reports')
    const srLinkText = django.gettext('Link to ')
    const publicText = django.gettext('public')
    const privateText = django.gettext('private')
    const semiPrivateText = django.gettext('semiprivate')

    if (!isLoaded) {
      return <div>{loadingText}</div>
    }

    return (
      <div className="row">
        <div className="col-12">
          <h3 className="mt-sm-0">Projects</h3>
          <ul className="pl-0">
            {items.map(item => (
              <li key={item.title} className="tile--sm tile--horizontal">
                <div className="tile__head">
                  <div className="tile__image tile__image--sm" style={{ backgroundImage: `url(${item.tile_image})` }}>
                    <div>{item.tile_image_copyright}</div>
                  </div>
                </div>
                <div className="tile__body">
                  <span className="text-muted">{byText}{item.organisation}</span>
                  <h3 className="tile__title mb-4">{item.offensive > 0 && <span className="text-info">• </span>}<a href={item.detail}>{item.title}</a></h3>
                  <div>
                    {item.access === 1 && <span className="label label--dark">{publicText}</span>}
                    {item.access === 2 && <span className="label label--dark">{semiPrivateText}</span>}
                    {item.access === 3 && <span className="label label--dark">{privateText}</span>}
                  </div>
                  <div className="row text-muted mt-3">
                    {item.offensive > 0 && <div className="col-4"><span className="fa-stack fa-2x" aria-hidden="true"><i className="fas fa-exclamation fa-stack-1x" /><i className="far fa-circle fa-stack-2x" /></span> {item.offensive} <span className="d-none d-lg-inline-block">{reportCountText}</span></div>}
                    {item.comment_count > 0 && <div className="col-4"><i className="far fa-comment" aria-hidden="true" /> {item.comment_count} <span className="d-none d-lg-inline-block">{commentCountText}</span></div>}
                    {item.future_phase && !item.active_phase && <div className="col-4"><i className="far fa-clock" aria-hidden="true" /> {item.participation_string}</div>}
                    {item.active_phase && <div className="col-4"><i className="far fa-clock" aria-hidden="true" /> <span className="d-inline-block d-lg-none">{this.getMobileTimespan(item)}</span> <span className="d-none d-lg-inline-block">{this.getTimespan(item)}</span></div>}
                    {item.past_phase && !item.active_phase && !item.future_phase && <div className="col-4"> {item.participation_string}</div>}
                  </div>
                  <a href={item.url} className="tile__link"><span className="sr-only">{srLinkText}{item.title}</span></a>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    )
  }
}
