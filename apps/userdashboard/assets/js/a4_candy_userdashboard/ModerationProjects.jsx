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

  render () {
    const { isLoaded, items } = this.state
    const loadingText = django.gettext('Loading...')
    const commentCountText = django.gettext(' comments')
    const reportCountText = django.gettext(' reports')
    const projectLengthText = django.gettext(' remaining')
    const srLinkText = django.gettext('Link to ')

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
                  <span className="text-muted">{item.organisation}</span>
                  <a href={item.url}><h3 className="tile__title mb-4">{item.title}</h3></a>
                  <div>
                    <span className="label label--dark">Project visibility</span>
                  </div>
                  <div className="d-flex justify-content-between text-muted mt-3">
                    <span><span className="fa-stack fa-2x" aria-hidden="true"><i className="fas fa-exclamation fa-stack-1x" /><i className="far fa-circle fa-stack-2x" /></span>{reportCountText}</span>
                    <span><i className="far fa-comment" aria-hidden="true" />{commentCountText}</span>
                    <span><i className="far fa-clock" aria-hidden="true" />{projectLengthText}</span>
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
