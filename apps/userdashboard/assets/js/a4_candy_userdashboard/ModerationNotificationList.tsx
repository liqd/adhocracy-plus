import React, { Component } from 'react'
import django from 'django'

import { ModerationNotification } from './ModerationNotification'
import { Filter } from './Filter'
import api from './api'
import type { FilterItem, ModerationItem } from './types'

const PACKET_COMMENT_SIZE = 15

interface ReviewCounts {
  unread: number
  read: number
  total: number
}

interface ModerationCounts {
  all: ReviewCounts
  comments: ReviewCounts
  reported: ReviewCounts
  ideas: ReviewCounts
}

const contentTypeFilterItems: FilterItem[] = [
  { label: django.gettext('All'), value: 'all' },
  { label: django.gettext('Comments'), value: 'comments' },
  { label: django.gettext('Reported comments'), value: 'reported' },
  { label: django.gettext('Ideas'), value: 'ideas' }
]

const readFilterItems: FilterItem[] = [
  { label: django.gettext('Unread'), value: 'False' },
  { label: django.gettext('Read'), value: 'True' },
  { label: django.gettext('All'), value: 'All' }
]

const orderingFilterItems: FilterItem[] = [
  { label: django.gettext('Oldest First'), value: 'created' },
  { label: django.gettext('Newest First'), value: '-created' },
  { label: django.gettext('Most reported'), value: '-num_reports' }
]

function formatCount (count: number): string {
  return String(count).padStart(2, '0')
}

interface ModerationNotificationListProps {
  moderationItemsApiUrl: string
  projectTitle: string
  organisation: string
  projectUrl: string
  ckeditorConfig?: string
}

interface ModerationNotificationListState {
  moderationItems: ModerationItem[]
  selectedFilters: {
    contentType: string
    isRead: string
    ordering: string
  }
  counts: ModerationCounts | null
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
      selectedFilters: {
        contentType: 'all',
        isRead: 'False',
        ordering: 'created'
      },
      counts: null,
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
      const data = await fetch(this.props.moderationItemsApiUrl + this.getUrlParams())
      const jsonData = await data.json()
      let counts = this.state.counts
      try {
        const countsData = await fetch(this.props.moderationItemsApiUrl + 'counts/')
        if (countsData.ok) {
          counts = await countsData.json()
        }
      } catch (error) {
        console.warn(error)
      }
      this.setState({
        moderationItems: jsonData.results,
        hasMore: jsonData.next,
        counts,
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

  markAllResolved = async () => {
    const [, error] = await api.fetch({
      url: this.props.moderationItemsApiUrl + 'mark_all_read/',
      method: 'POST'
    })
    if (error) {
      console.warn(error)
      return
    }
    this.loadDataWithFilter()
  }

  componentWillUnmount () {
    if (this.timer) {
      clearInterval(this.timer)
    }
    this.timer = null
  }

  getCurrentCounts (): ReviewCounts {
    if (!this.state.counts) {
      return { unread: 0, read: 0, total: 0 }
    }
    return this.state.counts[this.state.selectedFilters.contentType as keyof ModerationCounts] ||
      this.state.counts.all
  }

  getDisplayCount (): number {
    const counts = this.getCurrentCounts()
    if (this.state.selectedFilters.isRead === 'False') {
      return counts.unread
    }
    if (this.state.selectedFilters.isRead === 'True') {
      return counts.read
    }
    return counts.total
  }

  getDisplayLabel (): string {
    if (this.state.selectedFilters.isRead === 'False') {
      return django.gettext('Unread')
    }
    if (this.state.selectedFilters.isRead === 'True') {
      return django.gettext('Read')
    }
    return django.gettext('All')
  }

  render () {
    const { isLoaded } = this.state
    const { projectTitle, organisation, projectUrl, ckeditorConfig } = this.props
    const byText = django.gettext('By ')
    const loadmoreText = django.gettext('Load more')
    const gotoTopText = django.gettext('Go to top')
    const listText = django.gettext('Notifications of comments and ideas from project')
    const filterText = django.gettext('Notification filters and sorting')
    const headerText = django.gettext('Moderation project')
    const readFilterLabel = django.gettext('Read status')
    const typeFilterText = django.gettext('Type')
    const sortFilterText = django.gettext('Sort')
    const markAllResolvedText = django.gettext('Mark all as resolved')

    const counts = this.getCurrentCounts()
    const allUnreadCount = this.state.counts ? this.state.counts.all.unread : 0

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
          className="row align-items-center"
          aria-label={filterText}
        >
          <div className="col-12 col-lg-auto mb-2 mb-lg-0">
            <div className="moderation-filter" role="group" aria-label={readFilterLabel}>
              {readFilterItems.map(filter => {
                const count = filter.value === 'False'
                  ? counts.unread
                  : filter.value === 'True' ? counts.read : counts.total
                return (
                  <button
                    key={filter.value}
                    type="button"
                    className={
                      'moderation-filter__btn' +
                      (this.state.selectedFilters.isRead === filter.value ? ' is-active' : '')
                    }
                    aria-pressed={this.state.selectedFilters.isRead === filter.value}
                    onClick={() => this.isReadFilterChangeHandle(filter.value)}
                  >
                    {filter.label} ({formatCount(count)})
                  </button>
                )
              })}
            </div>
          </div>
          <div className="col-12 col-lg-auto mb-2 mb-lg-0">
            <Filter
              filterClass="moderation-projects__sort dropdown"
              filterItems={contentTypeFilterItems}
              onFilterChange={(value) => this.contentTypeFilterChangeHandle(value)}
              selectedFilter={this.state.selectedFilters.contentType}
              filterText={typeFilterText}
            />
          </div>
          <div className="col-12 col-lg-auto ms-lg-auto">
            <Filter
              filterClass="moderation-projects__sort dropdown"
              filterItems={orderingFilterItems}
              onFilterChange={(value) => this.orderingFilterChangeHandle(value)}
              selectedFilter={this.state.selectedFilters.ordering}
              filterText={sortFilterText}
            />
          </div>
        </nav>
        <div className="row align-items-center mb-2">
          <div className="col-12 col-lg-auto">
            <p className="moderation-projects__count u-text--gray mb-0">
              {formatCount(this.getDisplayCount())} {this.getDisplayLabel()}
            </p>
          </div>
          <div className="col-12 col-lg-auto ms-lg-auto">
            <button
              className="btn btn--light"
              type="button"
              onClick={this.markAllResolved}
              disabled={allUnreadCount === 0}
            >
              <i className="fas fa-box-archive" aria-hidden="true" />
              <span className="ms-2">{markAllResolvedText}</span>
            </button>
          </div>
        </div>
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
                  {this.state.moderationItems.map((item) => (
                    <ModerationNotification
                      key={item.item_type + '-' + item.pk}
                      notification={item}
                      apiUrl={item.api_url}
                      getUrlParams={() => this.getUrlParams()}
                      loadData={() => this.loadData()}
                      ckeditorConfig={ckeditorConfig}
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
