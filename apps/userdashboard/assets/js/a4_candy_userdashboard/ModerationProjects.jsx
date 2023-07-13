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
    this.isLoading = false
  }

  componentDidMount () {
    this.loadData()
    this.timer = setInterval(() => !this.isLoading && this.loadData(), 3000)
  }

  async loadData () {
    this.isLoading = true
    try {
      const data = await fetch(this.props.projectApiUrl)
      const jsonData = await data.json()
      jsonData.sort((a, b) => b.num_reported_unread_comments - a.num_reported_unread_comments)
      this.setState({
        items: jsonData,
        isLoaded: true
      })
    } catch (error) {
      console.warn(error)
    } finally {
      this.isLoading = false
    }
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
        <span>{item.active_phase[1]} {django.gettext('left')}</span>
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
    const publicText = django.gettext('public')
    const privateText = django.gettext('private')
    const semiPrivateText = django.gettext('semi-public')
    const hasUnReadComments = django.gettext('Notifications has unread comments')
    const overviewText = django.gettext('Moderation dashboard overview')
    const projectText = django.gettext('Projects')
    const projectSrText = django.gettext('Projects I am moderating')

    if (!isLoaded) {
      return <div>{loadingText}</div>
    }

    return (
      <>
        <h1 className="visually-hidden">
          {overviewText}
        </h1>
        <section className="row" aria-labelledby="sr-following-header">
          <div className="col-12">
            <h2 className="mt-sm-0">
              <span id="sr-following-header" className="visually-hidden">{projectSrText}</span>
              {projectText}
            </h2>
            <ul className="ps-0">
              {items.map(item => (
                <li key={item.title} className="tile tile--horizontal">
                  <a
                    href={item.moderation_detail_url}
                    className="tile__link"
                  >
                    <h3 className="visually-hidden">
                      {item.title}
                    </h3>
                    {item.num_unread_comments > 0 && <span className="text-info">• <span className="visually-hidden">{hasUnReadComments}</span></span>}
                  </a>
                  <div className="tile__head tile__head--wide">
                    <div
                      className="tile__image  tile__image--fill tile__image--sm"
                      style={{ backgroundImage: 'url(' + item.tile_image + ')' }}
                    >
                      <div className="tile__image__copyright copyright">
                        {item.tile_image_copyright}
                      </div>
                    </div>
                  </div>
                  <div className="tile__body">
                    <div>
                      <span className="u-text--gray">{byText}{item.organisation}</span>
                      <h3 className="tile__title mb-2">
                        {item.title}
                      </h3>
                      {item.access === 1 && <span className="badge badge--dark">{publicText}</span>}
                      {item.access === 2 && <span className="badge badge--dark">{semiPrivateText}</span>}
                      {item.access === 3 && <span className="badge badge--dark">{privateText}</span>}
                    </div>
                    <div className="row u-text--gray mt-3">
                      {item.num_reported_unread_comments > 0 && <div className="col-4"><i className="fas fa-exclamation-circle me-1" aria-hidden="true" /> {item.num_reported_unread_comments} <span className="d-none d-lg-inline-block">{reportCountText}</span></div>}
                      {item.comment_count > 0 && <div className="col-4"><i className="far fa-comment" aria-hidden="true" /> {item.comment_count} <span className="d-none d-lg-inline-block">{commentCountText}</span></div>}
                      {item.future_phase && !item.active_phase && <div className="col-4"><i className="far fa-clock" aria-hidden="true" /> {item.participation_string}</div>}
                      {item.active_phase && <div className="col-4"><i className="far fa-clock" aria-hidden="true" /> <span className="d-inline-block d-lg-none">{this.getMobileTimespan(item)}</span> <span className="d-none d-lg-inline-block">{this.getTimespan(item)}</span></div>}
                      {item.past_phase && !item.active_phase && !item.future_phase && <div className="col-4"> {item.participation_string}</div>}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </section>
      </>
    )
  }
}
