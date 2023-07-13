import React, { Component } from 'react'
import django from 'django'

import { ModerationNotification } from './ModerationNotification'
import { Filter } from './Filter'

const PACKET_COMMENT_SIZE = 15

const isReadFilterItems = [
  { label: django.gettext('Read'), value: 'True' },
  { label: django.gettext('Unread'), value: 'False' },
  { label: django.gettext('View all'), value: 'All' }
]

const reportsFilterItems = [
  { label: django.gettext('Reported'), value: 'True' },
  { label: django.gettext('All comments'), value: 'All' }
]

const orderingFilterItems = [
  { label: django.gettext('Most reported'), value: '-num_reports' },
  { label: django.gettext('Oldest'), value: 'created' },
  { label: django.gettext('Most recent'), value: '-created' }
]

export default class ModerationNotificationList extends Component {
  constructor (props) {
    super(props)

    this.state = {
      moderationComments: [],
      selectedFilters: { isRead: 'False', hasReports: 'All', ordering: '-num_reports' },
      numOfComments: PACKET_COMMENT_SIZE,
      hasMore: null,
      packetFactor: 1,
      isLoaded: false
    }
    this.isLoading = false
  }

  componentDidMount () {
    this.loadData()
    this.timer = setInterval(() => !this.isLoading && this.loadData(), 3000)
  }

  isReadFilterChangeHandle (value) {
    this.setState({
      selectedFilters: {
        ...this.state.selectedFilters,
        isRead: value
      },
      isLoaded: false
    },
    this.loadDataWithFilter
    )
  }

  reportsFilterChangeHandle (value) {
    this.setState({
      selectedFilters: {
        ...this.state.selectedFilters,
        hasReports: value
      },
      isLoaded: false
    },
    this.loadDataWithFilter
    )
  }

  orderingFilterChangeHandle (value) {
    this.setState({
      selectedFilters: {
        ...this.state.selectedFilters,
        ordering: value
      },
      isLoaded: false
    },
    this.loadDataWithFilter
    )
  }

  getUrlParams () {
    return '?is_reviewed=' + this.state.selectedFilters.isRead +
      '&has_reports=' + this.state.selectedFilters.hasReports +
      '&ordering=' + this.state.selectedFilters.ordering +
      '&num_of_comments=' + this.state.numOfComments
  }

  async loadData () {
    this.isLoading = true
    try {
      const url = this.props.moderationCommentsApiUrl + this.getUrlParams()
      const data = await fetch(url)
      const jsonData = await data.json()
      this.setState({
        moderationComments: jsonData.results,
        hasMore: jsonData.next,
        isLoaded: true
      })
    } catch (error) {
      console.warn(error)
    } finally {
      this.isLoading = false
    }
  }

  loadDataWithFilter () {
    this.setState(prevState => {
      return {
        ...prevState,
        numOfComments: PACKET_COMMENT_SIZE,
        packetFactor: 1
      }
    }, this.loadData)
  }

  handleAlert = (message, type = 'Notification') => {
    const alertMessage = typeof message === 'string'
      ? this.getSuccessAlert(message, type)
      : this.getErrorAlert(message)

    this.setState({
      alert: {
        ...alertMessage,
        onClick: () => this.hideAlert()
      }
    })
  }

  handleLoadMore = () => {
    this.setState(prevState => {
      const newPacketFactor = prevState.packetFactor + 1
      return {
        ...prevState,
        numOfComments: newPacketFactor * PACKET_COMMENT_SIZE,
        packetFactor: newPacketFactor
      }
    }, this.loadData)
  }

  handleToTop = () => {
    document.body.scrollTop = 0
    document.documentElement.scrollTop = 0
  }

  getSuccessAlert = (message) => {
    return {
      type: 'success',
      message
    }
  }

  getErrorAlert = (error) => {
    return {
      type: 'error',
      message: error.message
    }
  }

  hideAlert = () => {
    this.setState({ alert: undefined })
  }

  componentWillUnmount () {
    clearInterval(this.timer)
    this.timer = null
  }

  render () {
    const { isLoaded } = this.state
    const { projectTitle, organisation, projectUrl } = this.props
    const byText = django.gettext('By ')
    const loadmoreText = django.gettext('Load more')
    const gotoTopText = django.gettext('Go to top')
    const listText = django.gettext('Notifications of comments from project')
    const filterText = django.gettext('Notification filters and sorting')
    const headerText = django.gettext('Moderation project')

    return (
      <>
        <div className="row mb-2">
          <div className="col-12">
            <h1 className="visually-hidden">{headerText}</h1>
            <h2 className="mt-2">
              <a href={projectUrl}>{projectTitle}</a>
            </h2>
            <span className="u-text--gray">
              {byText}
              {organisation}
            </span>
          </div>
        </div>

        <nav
          className="row"
          aria-label={filterText}
        >
          <div className="col-md">
            <Filter
              filterClass="filter--full dropdown dropdown-menu-end"
              filterItems={reportsFilterItems}
              onFilterChange={(value) => this.reportsFilterChangeHandle(value)}
              selectedFilter={this.state.selectedFilters.hasReports}
              filterText={django.gettext('Filter')}
            />
          </div>
          <div className="col-md">
            <Filter
              filterClass="filter--full dropdown dropdown-menu-end"
              filterItems={isReadFilterItems}
              onFilterChange={(value) => this.isReadFilterChangeHandle(value)}
              selectedFilter={this.state.selectedFilters.isRead}
              filterText={django.gettext('Filter')}
            />
          </div>
          <div className="col-md">
            <Filter
              filterClass="filter--full dropdown dropdown-menu-end"
              filterItems={orderingFilterItems}
              onFilterChange={(value) => this.orderingFilterChangeHandle(value)}
              selectedFilter={this.state.selectedFilters.ordering}
              filterText={django.gettext('Sorting')}
            />
          </div>
        </nav>
        <section aria-labelledby="list-header" className="row">
          {!isLoaded
            ? (
              <div className="d-flex justify-content-center">
                <i className="fa fa-spinner fa-pulse" aria-hidden="true" />
              </div>
              )
            : (
              <div>
                <h3 id="list-header" className="visually-hidden">{listText}</h3>
                <ul className="u-list-reset">
                  {this.state.moderationComments.map((item, i) => (
                    <ModerationNotification
                      key={i}
                      notification={item}
                      apiUrl={this.props.moderationCommentsApiUrl + item.pk + '/'}
                      getUrlParams={() => this.getUrlParams()}
                      loadData={() => this.loadData()}
                    />
                  ))}
                </ul>
                <div className="d-flex justify-content-between">
                  {this.state.hasMore &&
                    <button
                      className="btn btn--light ms-auto"
                      onClick={this.handleLoadMore}
                    >
                      {loadmoreText}
                    </button>}
                  <button
                    className="btn btn--light ms-auto"
                    onClick={this.handleToTop}
                  >
                    <i className="fa fa-arrow-up" aria-hidden="true" />
                    <span className="visually-hidden">{gotoTopText}</span>
                  </button>
                </div>
              </div>)}
        </section>
      </>
    )
  }
}
