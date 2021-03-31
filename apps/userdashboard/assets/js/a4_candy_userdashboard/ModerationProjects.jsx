/* global fetch */
import React from 'react'

export default class ModerationProjects extends React.Component {
  constructor (props) {
    super(props)

    this.state = {
      items: [],
      isLoaded: false
    }
  }

  componentDidMount () {
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

  render () {
    const { isLoaded, items } = this.state

    if (!isLoaded) {
      return <div>Loading...</div>
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
                    <span><span class="fa-stack fa-2x" aria-hidden="true"><i className="fas fa-exclamation fa-stack-1x" /><i class="far fa-circle fa-stack-2x" /></span> amount of reports</span>
                    <span><i className="far fa-comment" aria-hidden="true" /> amount of comments</span>
                    <span><i className="far fa-clock" aria-hidden="true" /> time remaining</span>
                  </div>
                  <a href={item.url} className="tile__link"><span className="sr-only">Link to {item.title}</span></a>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    )
  }
}
