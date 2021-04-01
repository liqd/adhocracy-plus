/* global fetch */
import React from 'react'
import django from 'django'

export default class ModerationProjects extends React.Component {
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
        <span>{django.gettext('More than 1 year remaining')}</span>
      )
    } else {
      return (
        <span>{django.gettext('remaining')} {item.active_phase[1]}</span>
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
    const privateText = django.gettext('private')
    const semiPrivateText = django.gettext('semiprivate')

    if (!isLoaded) {
      return <div>{loadingText}</div>
    }

    return (
      <div className="row mb-2">
        <h2>Projects</h2>
        <div id="project_list">
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
                  <a href={item.url}><h3 className="tile__title mb-4">{item.title}</h3></a>
                  <div>
                    {item.access === 2 && <span className="label label--dark">{semiPrivateText}</span>}
                    {item.access === 3 && <span className="label label--dark">{privateText}</span>}
                  </div>
                  <div className="row text-muted mt-3">
                    {item.offensive > 0 && <div className="col-4"><span className="fa-stack fa-2x" aria-hidden="true"><i className="fas fa-exclamation fa-stack-1x" /><i className="far fa-circle fa-stack-2x" /></span> {item.offensive}{reportCountText}</div>}
                    {item.comment_count > 0 && <div className="col-4"><i className="far fa-comment" aria-hidden="true" /> {item.comment_count}{commentCountText}</div>}
                    {item.future_phase && !item.active_phase && <div className="col-4"><i className="far fa-clock" aria-hidden="true" /> {item.participation_string}</div>}
                    {item.active_phase && <div className="col-4"><i className="far fa-clock" aria-hidden="true" /> {this.getTimespan(item)}</div>}
                    {item.past_phase && !item.active_phase && !item.future_phase && <div className="col-4" />}
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
