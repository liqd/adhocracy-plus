import React, { Component } from 'react'
import django from 'django'
import { Filter } from './Filter'
import type { FilterItem } from './types'

function formatCount (count: number): string {
  return String(count).padStart(2, '0')
}

type StatusFilter = 'open' | 'resolved' | 'all'

interface ModerationProjectItem {
  id: number
  title: string
  moderation_detail_url: string
  num_unread_comments: number
  num_unread_items: number
  tile_image?: string
  tile_image_copyright?: string
  organisation: string
  access: number
  num_reported_unread_comments: number
  comment_count: number
  created: string
  future_phase?: boolean
  active_phase?: [unknown, string]
  past_phase?: boolean
  participation_string?: string
}

interface ModerationProjectsProps {
  projectApiUrl: string
}

interface ModerationProjectsState {
  items: ModerationProjectItem[]
  isLoaded: boolean
  searchQuery: string
  sortBy: string
  statusFilter: StatusFilter
}

export default class ModerationProjects extends Component<ModerationProjectsProps, ModerationProjectsState> {
  isLoading = false
  timer: ReturnType<typeof setInterval> | null = null

  constructor (props: ModerationProjectsProps) {
    super(props)

    this.state = {
      items: [],
      isLoaded: false,
      searchQuery: this.getInitialSearchQuery(),
      sortBy: this.getInitialSortBy(),
      statusFilter: this.getInitialStatusFilter()
    }
  }

  componentDidMount () {
    this.loadData()
    this.timer = setInterval(() => !this.isLoading && this.loadData(), 3000)
  }

  async loadData () {
    this.isLoading = true
    try {
      const data = await fetch(this.props.projectApiUrl)
      const jsonData = await data.json()
      this.setState({
        items: jsonData,
        isLoaded: true
      })
    } catch (error) {
      console.warn(error)
    } finally {
      this.isLoading = false
    }
  }

  componentWillUnmount () {
    if (this.timer) {
      clearInterval(this.timer)
    }
    this.timer = null
  }

  getUrlParam (name: string): string | null {
    const params = new URLSearchParams(window.location.search)
    return params.get(name)
  }

  setUrlParam (name: string, value: string): void {
    const url = new URL(window.location.href)
    if (value) {
      url.searchParams.set(name, value)
    } else {
      url.searchParams.delete(name)
    }
    window.history.replaceState({}, '', url.toString())
  }

  getInitialSortBy (): string {
    const sort = this.getUrlParam('sort')
    if (sort === 'recent') {
      return 'newest'
    }
    if (sort && ['oldest', 'newest', 'reports', 'name'].includes(sort)) {
      return sort
    }
    return 'oldest'
  }

  getInitialStatusFilter (): StatusFilter {
    const status = this.getUrlParam('status')
    if (status && ['open', 'resolved', 'all'].includes(status)) {
      return status as StatusFilter
    }
    return 'open'
  }

  getInitialSearchQuery (): string {
    return this.getUrlParam('search') || ''
  }

  getOpenItems (): ModerationProjectItem[] {
    return this.state.items.filter(item => item.num_unread_items > 0)
  }

  getResolvedItems (): ModerationProjectItem[] {
    return this.state.items.filter(item => item.num_unread_items === 0)
  }

  getStatusFilteredItems (): ModerationProjectItem[] {
    if (this.state.statusFilter === 'open') {
      return this.getOpenItems()
    }
    if (this.state.statusFilter === 'resolved') {
      return this.getResolvedItems()
    }
    return this.state.items
  }

  changeStatusFilter (statusFilter: StatusFilter): void {
    this.setUrlParam('status', statusFilter)
    this.setState({ statusFilter })
  }

  getTimespan (item: ModerationProjectItem) {
    const timeRemaining = item.active_phase?.[1].split(' ') || []
    const daysRemaining = parseInt(timeRemaining[0] || '0')
    if (daysRemaining > 365) {
      return (
        <span>{django.gettext('Over 1 year left')}</span>
      )
    } else {
      return (
        <span>{item.active_phase?.[1]} {django.gettext('left')}</span>
      )
    }
  }

  getMobileTimespan (item: ModerationProjectItem) {
    const timeRemaining = item.active_phase?.[1].split(' ') || []
    const daysRemaining = parseInt(timeRemaining[0] || '0')
    if (daysRemaining > 365) {
      return (
        <span>{django.gettext('1 year')}</span>
      )
    } else {
      return (
        <span>{item.active_phase?.[1]}</span>
      )
    }
  }

  getFilteredAndSortedItems (): ModerationProjectItem[] {
    const query = this.state.searchQuery.toLowerCase()

    const filtered = this.getStatusFilteredItems().filter(item => {
      const title = item.title ? item.title.toLowerCase() : ''
      const organisation = item.organisation ? item.organisation.toLowerCase() : ''
      return title.includes(query) || organisation.includes(query)
    })

    return filtered.sort((a, b) => {
      if (this.state.sortBy === 'oldest') {
        return new Date(a.created).getTime() - new Date(b.created).getTime()
      }
      if (this.state.sortBy === 'newest') {
        return new Date(b.created).getTime() - new Date(a.created).getTime()
      }
      if (this.state.sortBy === 'reports') {
        return b.num_reported_unread_comments - a.num_reported_unread_comments
      }
      if (this.state.sortBy === 'name') {
        return a.title.localeCompare(b.title)
      }
      return 0
    })
  }

  render () {
    const { isLoaded } = this.state
    const loadingText = django.gettext('Loading...')
    const byText = django.gettext('By ')
    const commentCountText = django.gettext(' comments')
    const reportCountText = django.gettext(' reports')
    const publicText = django.gettext('public')
    const privateText = django.gettext('private')
    const semiPrivateText = django.gettext('semi-public')
    const hasUnReadComments = django.gettext('Notifications has unread comments')
    const searchPlaceholder = django.gettext('Search')
    const sortLabel = django.gettext('Sort')
    const statusFilterLabel = django.gettext('Moderation status')
    const emptyText = django.gettext('No moderated projects found.')

    if (!isLoaded) {
      return <div>{loadingText}</div>
    }

    const openCount = this.getOpenItems().length
    const resolvedCount = this.getResolvedItems().length
    const allCount = this.state.items.length
    const items = this.getFilteredAndSortedItems()
    const projectCountText = django.ngettext('Project', 'Projects', items.length)
    const statusFilters: { value: StatusFilter, label: string, count: number }[] = [
      { value: 'open', label: django.gettext('Open'), count: openCount },
      { value: 'resolved', label: django.gettext('Resolved'), count: resolvedCount },
      { value: 'all', label: django.gettext('All'), count: allCount }
    ]
    const sortItems: FilterItem[] = [
      { value: 'oldest', label: django.gettext('Oldest First') },
      { value: 'newest', label: django.gettext('Newest First') },
      { value: 'reports', label: django.gettext('Most reported') },
      { value: 'name', label: django.gettext('Alphabetical') }
    ]

    return (
      <>
        <section className="row">
          <div className="col-12">
            <div className="moderation-projects__filters row align-items-center mb-2">
              <div className="col-12 col-md-auto mb-2 mb-md-0">
                <div
                  className="moderation-filter"
                  role="group"
                  aria-label={statusFilterLabel}
                >
                  {statusFilters.map(filter => (
                    <button
                      key={filter.value}
                      type="button"
                      className={
                        'moderation-filter__btn' +
                        (this.state.statusFilter === filter.value ? ' is-active' : '')
                      }
                      aria-pressed={this.state.statusFilter === filter.value}
                      onClick={() => this.changeStatusFilter(filter.value)}
                    >
                      {filter.label} ({formatCount(filter.count)})
                    </button>
                  ))}
                </div>
              </div>
              <div className="col-12 col-md-auto ms-md-auto">
                <Filter
                  filterClass="moderation-projects__sort dropdown"
                  filterItems={sortItems}
                  selectedFilter={this.state.sortBy}
                  onFilterChange={(sortBy) => {
                    this.setUrlParam('sort', sortBy)
                    this.setState({ sortBy })
                  }}
                  filterText={sortLabel}
                />
              </div>
            </div>

            <div className="row align-items-center mb-3">
              <div className="col-12 col-md-auto">
                <p className="moderation-projects__count u-text--gray mb-0">
                  {items.length} {projectCountText}
                </p>
              </div>
              <div className="col-12 col-md-4 ms-md-auto mt-2 mt-md-0">
                <input
                  type="search"
                  className="form-control"
                  placeholder={searchPlaceholder}
                  aria-label={searchPlaceholder}
                  value={this.state.searchQuery}
                  onChange={(e) => {
                    // Stop the native change event from reaching the
                    // document-level listener in unload_warning.js, which
                    // would arm the unsaved-changes warning for these
                    // read-only controls.
                    e.nativeEvent.stopImmediatePropagation()
                    const searchQuery = e.target.value
                    this.setUrlParam('search', searchQuery)
                    this.setState({ searchQuery })
                  }}
                />
              </div>
            </div>

            {items.length === 0
              ? <p>{emptyText}</p>
              : (
                <ul className="ps-0">
                  {items.map(item => (
                    <li key={item.id} className="tile tile--horizontal">
                      <a
                        href={item.moderation_detail_url}
                        className="tile__link"
                      >
                        <h3 className="visually-hidden">
                          {item.title}
                        </h3>
                        {item.num_unread_comments > 0 && <span className="text-info">• <span className="visually-hidden">{hasUnReadComments}</span></span>}
                      </a>
                      <div className="tile__head tile__head--wide">
                        <div
                          className="tile__image  tile__image--fill tile__image--sm"
                          style={{ backgroundImage: 'url(' + item.tile_image + ')' }}
                        >
                          <div className="tile__image__copyright copyright">
                            {item.tile_image_copyright}
                          </div>
                        </div>
                      </div>
                      <div className="tile__body">
                        <div>
                          <span className="u-text--gray">{byText}{item.organisation}</span>
                          <h3 className="tile__title mb-2">
                            {item.title}
                          </h3>
                          {item.access === 1 && <span className="badge badge--dark">{publicText}</span>}
                          {item.access === 2 && <span className="badge badge--dark">{semiPrivateText}</span>}
                          {item.access === 3 && <span className="badge badge--dark">{privateText}</span>}
                        </div>
                        <div className="row u-text--gray mt-3">
                          {item.num_reported_unread_comments > 0 && <div className="col-4"><i className="fas fa-exclamation-circle me-1" aria-hidden="true" /> {item.num_reported_unread_comments} <span className="d-none d-lg-inline-block">{reportCountText}</span></div>}
                          {item.comment_count > 0 && <div className="col-4"><i className="far fa-comment" aria-hidden="true" /> {item.comment_count} <span className="d-none d-lg-inline-block">{commentCountText}</span></div>}
                          {item.future_phase && !item.active_phase && <div className="col-4"><i className="far fa-clock" aria-hidden="true" /> {item.participation_string}</div>}
                          {item.active_phase && <div className="col-4"><i className="far fa-clock" aria-hidden="true" /> <span className="d-inline-block d-lg-none">{this.getMobileTimespan(item)}</span> <span className="d-none d-lg-inline-block">{this.getTimespan(item)}</span></div>}
                          {item.past_phase && !item.active_phase && !item.future_phase && <div className="col-4"> {item.participation_string}</div>}
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
                )}
          </div>
        </section>
      </>
    )
  }
}
