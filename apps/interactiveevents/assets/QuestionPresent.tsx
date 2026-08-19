import React from 'react'
import django from 'django'
import type { LikeInfo } from './types'

interface QuestionPresentProps {
  id?: number
  likes: LikeInfo
  children?: React.ReactNode
}

interface QuestionPresentState {
  likes: number
}

export default class QuestionPresent extends React.Component<QuestionPresentProps, QuestionPresentState> {
  constructor (props: QuestionPresentProps) {
    super(props)

    this.state = {
      likes: this.props.likes.count
    }
  }

  componentDidUpdate (prevProps: QuestionPresentProps) {
    if (this.props.likes !== prevProps.likes) {
      this.setState({
        likes: this.props.likes.count
      })
    }
  }

  handleErrors (response: Response) {
    if (!response.ok) {
      throw Error(response.statusText)
    }
    return response
  }

  render () {
    const likesTag = django.gettext('likes')
    return (
      <div className="col-md-8 offset-2">
        <div className="list-item mb-2">
          <div>
            <p>{this.props.children}</p>
          </div>
          <div className="row">
            <div className="col-12">
              <div>
                <div className="float-right">
                  <span className="text-muted">{this.state.likes}</span>
                  <i className="icon-like text-muted ms-2" aria-hidden="true" />
                  <span className="visually-hidden">{likesTag}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }
}
