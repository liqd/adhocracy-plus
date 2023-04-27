import django from 'django'
import React from 'react'
import { updateItem } from './helpers.js'
import QuestionForm from './QuestionForm'
import QuestionList from './QuestionList'
import InfoBox from './InfoBox'
import Filter from './Filters'
import StatisticsBox from './StatisticsBox'

const textStatistics = django.gettext('Statistics')
const textQuestionCount = django.gettext('Entries')
const ariaOpenStatistics = django.gettext('Click to view statistics of answered questions')
const textDisplayOnScreen = django.gettext('display on screen')
const ariaDisplayOnScreen = django.gettext('Click to view list of marked questions screen')

export default class QuestionBox extends React.Component {
  constructor (props) {
    super(props)

    this.restartPolling = this.restartPolling.bind(this)

    this.state = {
      questions: [],
      filteredQuestions: [],
      answeredQuestions: [],
      category: '-1',
      categoryName: django.gettext('select affiliation'),
      displayNotHiddenOnly: false,
      displayOnShortlist: false,
      orderedByLikes: false,
      filterChanged: false,
      orderingChanged: false,
      pollingPaused: false,
      showStatistics: false,
      questionCount: 0
    }
  }

  componentDidMount () {
    this.restartPolling()
  }

  componentWillUnmount () {
    this.timer = null
  }

  componentDidUpdate () {
    if (this.state.filterChanged === true) {
      this.updateList()
    }
    if (this.state.orderingChanged === true) {
      this.getItems()
    }
  }

  setCategory (category) {
    const newName = (category === '-1') ? django.gettext('all') : category
    this.setState({
      filterChanged: true,
      categoryName: newName,
      category
    })
  }

  toggledisplayNotHiddenOnly () {
    const displayNotHiddenOnly = !this.state.displayNotHiddenOnly
    this.setState({
      filterChanged: true,
      displayNotHiddenOnly
    })
  }

  toggleDisplayOnShortlist () {
    const displayOnShortlist = !this.state.displayOnShortlist
    this.setState({
      filterChanged: true,
      displayOnShortlist
    })
  }

  toggleOrdering () {
    const orderedByLikes = !this.state.orderedByLikes
    this.setState({
      orderingChanged: true,
      orderedByLikes
    })
  }

  handleToggleStatistics () {
    const newValue = !this.state.showStatistics
    this.setState({
      showStatistics: newValue
    })
  }

  isInFilter (item) {
    return (this.state.category === '-1' || this.state.category === item.category) &&
      (!this.state.displayOnShortlist || item.is_on_shortlist) && (!this.state.displayNotHiddenOnly || !item.is_hidden)
  }

  filterQuestions (questions) {
    const filteredQuestions = []
    questions.forEach((item) => {
      if (this.isInFilter(item) && !item.is_answered) {
        filteredQuestions.push(item)
      }
    })
    return filteredQuestions
  }

  getAnsweredQuestions (questions) {
    const answeredQuestions = []
    questions.forEach((item) => {
      if (item.is_answered) {
        answeredQuestions.push(item)
      }
    })
    return answeredQuestions
  }

  updateList () {
    const filteredQuestions = this.filterQuestions(this.state.questions)
    this.setState({
      filterChanged: false,
      filteredQuestions
    })
  }

  getUrl () {
    const url = this.props.questions_api_url
    if (this.state.orderedByLikes) {
      return url + '?ordering=-like_count'
    }
    return url
  }

  getItems () {
    if (!this.state.pollingPaused) {
      fetch(this.getUrl())
        .then(response => response.json())
        .then(data => this.setState({
          questions: data,
          filteredQuestions: this.filterQuestions(data),
          answeredQuestions: this.getAnsweredQuestions(data),
          orderingChanged: false,
          questionCount: this.filterQuestions(data).length
        }))
    }
  }

  updateQuestion (data, id) {
    this.setState({
      pollingPaused: true
    })
    const url = this.props.questions_api_url + id + '/'
    return updateItem(data, url, 'PATCH')
  }

  removeFromList (id, data) {
    this.updateQuestion(data, id)
      .then(response => this.setState(prevState => ({
        filteredQuestions: prevState.filteredQuestions.filter(question => question.id !== id),
        pollingPaused: false
      })))
  }

  handleLike (id, value) {
    const url = this.props.likes_api_url.replace('LIVEQUESTIONID', id)
    const data = { value }
    return updateItem(data, url, 'POST')
  }

  togglePollingPaused () {
    const pollingPaused = !this.state.pollingPaused
    this.setState({
      pollingPaused
    })
  }

  restartPolling () {
    this.getItems()
    clearInterval(this.timer)
    this.timer = setInterval(() => this.getItems(), 5000)
  }

  render () {
    return (
      <div>
        {this.props.hasAskQuestionsPermission &&
          <QuestionForm
            restartPolling={this.restartPolling}
            category_dict={this.props.category_dict}
            questions_api_url={this.props.questions_api_url}
            privatePolicyLabel={this.props.privatePolicyLabel}
            termsOfUseUrl={this.props.termsOfUseUrl}
            dataProtectionPolicyUrl={this.props.dataProtectionPolicyUrl}
          />}
        <div>
          <div className={this.props.isModerator ? 'livequestion__control-bar--mod' : 'livequestion__control-bar--user'}>
            <div className="livequestion__action-bar">
              {this.props.isModerator &&
                <div className="livequestion__action-bar--btn pe-lg-3">
                  <a
                    className="btn btn--light"
                    rel="noopener noreferrer"
                    href={this.props.present_url}
                    target="_blank"
                    aria-label={ariaDisplayOnScreen}
                    title={ariaDisplayOnScreen}
                  >
                    <span className="fa-stack fa-1x me-1">
                      <i className="fas fa-tv fa-stack-2x" aria-label="hidden"> </i>
                      <i className="fas fa-arrow-up fa-stack-1x" aria-label="hidden"> </i>
                    </span>
                    {textDisplayOnScreen}
                  </a>
                </div>}
              <div className="livequestion__action-bar--btn pe-xl-3">
                <div className="checkbox-btn">
                  <label
                    htmlFor="displayStatistics"
                    className="checkbox-btn__label--light"
                    title={ariaOpenStatistics}
                    aria-label={ariaOpenStatistics}
                  >
                    <input
                      className="checkbox-btn__input"
                      type="checkbox"
                      id="displayStatistics"
                      onChange={this.handleToggleStatistics.bind(this)}
                      checked={this.state.showStatistics}
                    />
                    <span className="checkbox-btn__text--colour">
                      <i className="fas fa-chart-bar me-1" aria-label="hidden" />
                      {textStatistics}
                    </span>
                  </label>
                </div>
              </div>
            </div>
            {!this.state.showStatistics &&
              <Filter
                categories={this.props.categories}
                currentCategory={this.state.category}
                currentCategoryName={this.state.categoryName}
                setCategories={this.setCategory.bind(this)}
                orderedByLikes={this.state.orderedByLikes}
                toggleOrdering={this.toggleOrdering.bind(this)}
                displayOnShortlist={this.state.displayOnShortlist}
                displayNotHiddenOnly={this.state.displayNotHiddenOnly}
                toggleDisplayOnShortlist={this.toggleDisplayOnShortlist.bind(this)}
                toggledisplayNotHiddenOnly={this.toggledisplayNotHiddenOnly.bind(this)}
                isModerator={this.props.isModerator}
              />}
          </div>
          {!this.state.showStatistics &&
            <div className="livequestion__info-box-parent">
              <InfoBox
                isModerator={this.props.isModerator}
              />
              <label className="livequestion__count">{this.state.questionCount} {textQuestionCount}</label>
            </div>}

          {this.state.showStatistics &&
            <div
              className="mt-3 u-border"
              id="livequestion-statistics"
              aria-hidden="false"
            >
              <button type="button" className="livequestion__close" onClick={this.handleToggleStatistics.bind(this)}>
                <span aria-label="close">&times;</span>
              </button>
              <StatisticsBox
                answeredQuestions={this.state.answeredQuestions}
                questions_api_url={this.props.questions_api_url}
                categories={this.props.categories}
                isModerator={this.props.isModerator}
              />
            </div>}
          {!this.state.showStatistics &&
            <QuestionList
              questions={this.state.filteredQuestions}
              removeFromList={this.removeFromList.bind(this)}
              updateQuestion={this.updateQuestion.bind(this)}
              handleLike={this.handleLike.bind(this)}
              isModerator={this.props.isModerator}
              togglePollingPaused={this.togglePollingPaused.bind(this)}
              hasLikingPermission={this.props.hasLikingPermission}
            />}
        </div>
        <span className="livequestion_anchor" id="question-list-end" />
      </div>
    )
  }
}
