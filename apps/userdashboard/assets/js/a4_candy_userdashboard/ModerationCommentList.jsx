import React, { Component } from 'react'
import django from 'django'

import ModerationComment from './ModerationComment'

export default class ModerationCommentList extends Component {
  constructor (props) {
    super(props)

    this.state = {
      aiClassifications: [],
      userClassifications: [],
      isLoaded: false
    }
  }

  componentDidMount () {
    this.loadData()
    this.timer = setInterval(() => this.loadData(), 3000)
  }

  async loadData () {
    fetch(this.props.aiclassificationApiUrl)
      .then(res => res.json())
      .then(json => {
        this.setState({
          aiClassifications: json
        })
      }).catch((err) => {
        console.log(err)
      })
    fetch(this.props.userclassificationApiUrl)
      .then(res => res.json())
      .then(json => {
        this.setState({
          userClassifications: json,
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
    const { isLoaded, aiClassifications, userClassifications } = this.state
    const { projectTitle, organisation, projectUrl } = this.props
    const byText = django.pgettext('kosmo', 'By ')
    const loadingText = django.pgettext('kosmo', 'Loading...')

    if (!isLoaded) {
      return <div>{loadingText}</div>
    }

    return (
      <div className="row mb-2">
        <div className="col-12">
          <h1 className="m-0"><a href={projectUrl}>{projectTitle}</a></h1>
          <span className="text-muted">{byText}{organisation}</span>
          <ul className="pl-0 mt-5">
            {userClassifications.map((item, i) => (
              <li className="list-item" key={i}>
                <ModerationComment
                  classification={item.classification}
                  commentText={item.comment_text}
                  commentUrl={item.comment.comment_url}
                  created={item.created}
                  userImage={item.comment.user_image}
                  userName={item.comment.user_name}
                />
              </li>
            ))}
            {aiClassifications.map((item, i) => (
              <li className="list-item" key={i}>
                <ModerationComment
                  classification={item.classification}
                  commentText={item.comment_text}
                  commentUrl={item.comment.comment_url}
                  created={item.created}
                  userImage={item.comment.user_image}
                  userName={item.comment.user_name}
                  aiClassified
                />
              </li>
            ))}
          </ul>
        </div>
      </div>
    )
  }
}
