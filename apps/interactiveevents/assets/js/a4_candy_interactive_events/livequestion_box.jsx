import django from 'django'
import React from 'react'
import { updateItem } from './helpers.js'
import QuestionForm from './livequestion_form'
import QuestionList from './livequestion_list'
import InfoBox from './livequestion_info_box'
import Filter from './livequestion_filters'
import StatisticsBox from './livequestion_statistics_box'

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
    const newName = (category === '-1') ? django.gettext('select affiliation') : category
    this.setState({
      filterChanged: true,
      categoryName: newName,
      category: category
    })
  }

  toggledisplayNotHiddenOnly () {
    const displayNotHiddenOnly = !this.state.displayNotHiddenOnly
    this.setState({
      filterChanged: true,
      displayNotHiddenOnly: displayNotHiddenOnly
    })
  }

  toggleDisplayOnShortlist () {
    const displayOnShortlist = !this.state.displayOnShortlist
    this.setState({
      filterChanged: true,
      displayOnShortlist: displayOnShortlist
    })
  }

  toggleOrdering () {
    const orderedByLikes = !this.state.orderedByLikes
    this.setState({
      orderingChanged: true,
      orderedByLikes: orderedByLikes
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
      filteredQuestions: filteredQuestions
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
    const data = { value: value }
    return updateItem(data, url, 'POST')
  }

  togglePollingPaused () {
    const pollingPaused = !this.state.pollingPaused
    this.setState({
      pollingPaused: pollingPaused
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
        <div>
          <div className="container">
            {this.props.hasAskQuestionsPermission &&
              <div className="row mb-5">
                <div className="col-md-10 offset-md-1">
                  <QuestionForm
                    restartPolling={this.restartPolling}
                    category_dict={this.props.category_dict}
                    questions_api_url={this.props.questions_api_url}
                    privatePolicyLabel={this.props.privatePolicyLabel}
                    termsOfUseUrl={this.props.termsOfUseUrl}
                    dataProtectionPolicyUrl={this.props.dataProtectionPolicyUrl}
                  />
                </div>
              </div>}
            <div className="row mb-5">
              <div className="col-md-10 offset-md-1">
                <div className={'row ' + (this.props.isModerator ? 'livequestions__control-bar--mod' : 'livequestions__control-bar--user')}>
                  <div className="livequestions__action-bar">
                    {this.props.isModerator &&
                      <div className="livequestions__action-bar--btn">
                        <a
                          className="btn btn--light"
                          rel="noopener noreferrer"
                          href={this.props.present_url}
                          target="_blank"
                          aria-label={ariaDisplayOnScreen}
                          title={ariaDisplayOnScreen}
                        >
                          <span className="fa-stack fa-1x mr-1">
                            <i className="fas fa-tv fa-stack-2x" aria-label="hidden"> </i>
                            <i className="fas fa-arrow-up fa-stack-1x" aria-label="hidden"> </i>
                          </span>
                          {textDisplayOnScreen}
                        </a>
                      </div>}
                    <div className="livequestions__action-bar--btn pr-md-3">
                      <div className="btn--light checkbox-btn">
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
                          <span className="checkbox-btn__text">
                            <i className="fas fa-chart-bar mr-1" aria-label="hidden" />
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
                  <div className="row">
                    <div className="col">
                      <label className="livequestions__count">{this.state.questionCount} {textQuestionCount}</label>
                      <InfoBox
                        isModerator={this.props.isModerator}
                      />
                    </div>
                  </div>}

                {this.state.showStatistics &&
                  <div
                    className="mt-3 u-border"
                    id="livequestion-statistics"
                    aria-hidden="false"
                  >
                    <button type="button" className="close pr-2" onClick={this.handleToggleStatistics.bind(this)}>
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
            </div>
            <span className="livequestions_anchor" id="question-list-end" />
          </div>
        </div>
      </div>

    )
  }
}
