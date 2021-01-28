/* global fetch */
import React from 'react'

export default class ModerationProjects extends React.Component {
  constructor (props) {
    super(props)

    this.state = {
      projectTitle: [],
      organisation: [],
      url: [],
      projectImage: [],
      imageCopyright: []
    }
  }

  getProjectData (projectData) {
    let i = 0
    for (i = 0; i < projectData.length; i++) {
      var element = document.createElement('div')
      element.setAttribute('class', 'col-sm-6 col-lg-4')
      element.innerHTML = '<li class="tile organisation__tile userdashboard__tile">' + '<a href=' + projectData[i].url + '>' +
                          '<div class="tile__head">' + '<div class="tile__image tile__image--sm" style="background-image: url(' +
                          projectData[i].tile_image + ')">' + '</div>' + '</div>' + '<div class="tile__body">' +
                          '<span class="text-muted">' + projectData[i].organisation + '</span>' +
                          '<h3 class="tile__title mb-4">' + projectData[i].title + '</h3>' +
                          '<div>' + projectData[i].tile_image_copyright + '</div>' + '</a>' + '</li>'

      $('#project_list').append(element)
      this.setState({
        projectTitle: this.state.projectTitle.concat(projectData[i].title),
        organisation: this.state.organisation.concat(projectData[i].organisation),
        url: this.state.url.concat(projectData[i].url),
        projectImage: this.state.projectImage.concat(projectData[i].tile_image),
        imageCopyright: this.state.imageCopyright.concat(projectData[i].tile_image_copyright)
      })
    }
  }

  getItems () {
    fetch(this.props.projectApiUrl)
      .then((response) => {
        return response.json()
      }).then((data) => {
        this.getProjectData(data)
      })
  }

  componentDidMount () {
    this.getItems()
  }

  render () {
    return (
      <div className="row mb-2">
        <h2>Projects</h2>
        <div class="row" id="project_list" />
      </div>
    )
  }
}
