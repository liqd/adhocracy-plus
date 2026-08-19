import $ from 'jquery'
import React from 'react'
import QuestionPresent from './QuestionPresent'
import type { LikeInfo } from './types'

interface PresentQuestion {
  id: number
  text: string
  likes: LikeInfo
}

interface PresentBoxProps {
  questions_api_url: string
  title: string
}

interface PresentBoxState {
  questions: PresentQuestion[]
}

export default class PresentBox extends React.Component<PresentBoxProps, PresentBoxState> {
  timer: ReturnType<typeof setInterval> | null = null

  constructor (props: PresentBoxProps) {
    super(props)

    this.state = {
      questions: []
    }
  }

  getListAndFooter (data: PresentQuestion[]) {
    this.setState({
      questions: data
    })
    this.displayFooterOrInfo()
  }

  getItems () {
    fetch(this.props.questions_api_url + '?is_live=1&is_answered=0')
      .then(response => response.json())
      .then(data => this.getListAndFooter(data))
      .catch(() => {})
  }

  componentDidMount () {
    this.getItems()
    this.timer = setInterval(() => this.getItems(), 5000)
  }

  componentWillUnmount () {
    if (this.timer) {
      clearInterval(this.timer)
    }
    this.timer = null
  }

  displayFooterOrInfo () {
    if (this.state.questions.length > 0) {
      $('#id-present-infographic').removeClass('d-none')
      $('#id-present-infographic').addClass('infographic__info-footer')
      $('#id-present-infographic').removeClass('infographic__info-screen')
    } else {
      $('#id-present-infographic').removeClass('d-none')
      $('#id-present-infographic').removeClass('infographic__info-footer')
      $('#id-present-infographic').addClass('infographic__info-screen')
    }
  }

  render () {
    if (this.state.questions.length > 0) {
      return (
        <div className="container">
          <div className="list-group mt-5">
            {this.state.questions.map((question) => {
              return (
                <QuestionPresent
                  key={question.id}
                  id={question.id}
                  likes={question.likes}
                >
                  {question.text}
                </QuestionPresent>
              )
            })}
          </div>
        </div>
      )
    } else {
      return (
        <div className="row justify-content-center mt-5">
          <div className="col-8 text-center py-5">
            <h1 className="u-serif-header">{this.props.title}</h1>
          </div>
        </div>
      )
    }
  }
}
