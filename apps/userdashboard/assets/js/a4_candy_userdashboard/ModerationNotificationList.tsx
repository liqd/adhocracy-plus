import React, { Component } from 'react'
import django from 'django'

import { ModerationNotification } from './ModerationNotification'
import { Filter } from './Filter'
import type { FilterItem, ModerationItem } from './types'

const PACKET_COMMENT_SIZE = 15

const contentTypeFilterItems: FilterItem[] = [
  { label: django.gettext('All'), value: 'all' },
  { label: django.gettext('All comments'), value: 'comments' },
  { label: django.gettext('Reported comments'), value: 'reported' },
  { label: django.gettext('All ideas'), value: 'ideas' }
]

const isReadFilterItems: FilterItem[] = [
  { label: django.gettext('Read'), value: 'True' },
  { label: django.gettext('Unread'), value: 'False' },
  { label: django.gettext('View all'), value: 'All' }
]

const orderingFilterItems: FilterItem[] = [
  { label: django.gettext('Most reported'), value: '-num_reports' },
  { label: django.gettext('Oldest'), value: 'created' },
  { label: django.gettext('Most recent'), value: '-created' }
]

interface ModerationNotificationListProps {
  moderationItemsApiUrl: string
  projectTitle: string
  organisation: string
  projectUrl: string
}

interface ModerationNotificationListState {
  moderationItems: ModerationItem[]
  selectedFilters: {
    contentType: string
    isRead: string
    ordering: string
  }
  numOfComments: number
  hasMore: string | null
  packetFactor: number
  isLoaded: boolean
}

export default class ModerationNotificationList extends Component<ModerationNotificationListProps, ModerationNotificationListState> {
  isLoading = false
  timer: ReturnType<typeof setInterval> | null = null

  constructor (props: ModerationNotificationListProps) {
    super(props)

    this.state = {
      moderationItems: [],
      selectedFilters: { contentType: 'all', isRead: 'False', ordering: '-num_reports' },
      numOfComments: PACKET_COMMENT_SIZE,
      hasMore: null,
      packetFactor: 1,
      isLoaded: false
    }
  }

  componentDidMount () {
    this.loadData()
    this.timer = setInterval(() => !this.isLoading && this.loadData(), 3000)
  }

  contentTypeFilterChangeHandle (value: string) {
    this.setState({
      selectedFilters: {
        ...this.state.selectedFilters,
        contentType: value
      },
      isLoaded: false
    },
    this.loadDataWithFilter
    )
  }

  isReadFilterChangeHandle (value: string) {
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

  orderingFilterChangeHandle (value: string) {
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
    return '?content_type=' + this.state.selectedFilters.contentType +
      '&is_reviewed=' + this.state.selectedFilters.isRead +
      '&ordering=' + this.state.selectedFilters.ordering +
      '&num_of_comments=' + this.state.numOfComments
  }

  async loadData () {
    this.isLoading = true
    try {
      const url = this.props.moderationItemsApiUrl + this.getUrlParams()
      const data = await fetch(url)
      const jsonData = await data.json()
      this.setState({
        moderationItems: jsonData.results,
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

  componentWillUnmount () {
    if (this.timer) {
      clearInterval(this.timer)
    }
    this.timer = null
  }

  render () {
    const { isLoaded } = this.state
    const { projectTitle, organisation, projectUrl } = this.props
    const byText = django.gettext('By ')
    const loadmoreText = django.gettext('Load more')
    const gotoTopText = django.gettext('Go to top')
    const listText = django.gettext('Notifications of comments and ideas from project')
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
              filterItems={contentTypeFilterItems}
              onFilterChange={(value) => this.contentTypeFilterChangeHandle(value)}
              selectedFilter={this.state.selectedFilters.contentType}
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
                  {this.state.moderationItems.map((item, i) => (
                    <ModerationNotification
                      key={i}
                      notification={item}
                      apiUrl={item.api_url}
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
