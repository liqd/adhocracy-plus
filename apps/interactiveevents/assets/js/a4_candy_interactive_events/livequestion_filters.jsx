import React from 'react'
import django from 'django'

export default class Filter extends React.Component {
  constructor (props) {
    super(props)

    this.state = {
      showFilters: false
    }
  }

  selectCategory (e) {
    e.preventDefault()
    const category = e.target.getAttribute('data-value')
    this.props.setCategories(category)
  }

  getButtonClass () {
    if (this.props.currentCategory === '-1') {
      return 'dropdown-toggle btn btn--light btn--select'
    } else {
      return 'btn btn--secondary dropdown-toggle btn--select'
    }
  }

  handleToggleFilters () {
    const newValue = !this.state.showFilters
    this.setState({
      showFilters: newValue
    })
  }

  render () {
    const textFilters = django.gettext(' Filters')
    const ariaOpenFilters = django.gettext('Click to view filters')
    const allText = django.gettext('all')
    const ariaDisplayOnlyMarked = django.gettext('Click to only display marked questions')
    const ariaDisplayNotHidden = django.gettext('Click to only display questions which are not hidden')
    const ariaOrderLikes = django.gettext('Click to order list by likes')
    return (
      <div className={'livequestions__filter-bar ' + (this.state.showFilters && 'mb-5')}>
        <div className="dropdown livequestions__filter--btn">
          <button
            className={this.getButtonClass()} type="button" id="dropdownMenuButton"
            data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"
          >
            {this.props.currentCategoryName}
            <i className="fa fa-caret-down" aria-hidden="true" />
          </button>
          <div className="dropdown-menu" aria-labelledby="dropdownMenuButton">
            <button className="dropdown-item" data-value={-1} onClick={this.selectCategory.bind(this)} href="#">{allText}</button>
            {this.props.categories.map((category, index) => {
              return <button className="dropdown-item" key={index} data-value={category} onClick={this.selectCategory.bind(this)} href="#">{category}</button>
            })}
          </div>
        </div>
        {this.props.isModerator &&
          <div className="checkbox-btn livequestions__filter--btn pr-3">
            <label
              htmlFor="markedCheck"
              className="checkbox-btn__label--light"
              aria-label={ariaOpenFilters}
              title={ariaOpenFilters}
            >
              <input
                className="checkbox-btn__input"
                type="checkbox"
                id="markedCheck"
                name="markedCheck"
                checked={this.props.showFilters}
                onChange={this.handleToggleFilters.bind(this)} // eslint-disable-line react/jsx-handler-names
              />
              <span className="checkbox-btn__text">
                <i className="fas fa-sliders-h" aria-hidden="true" />
                {textFilters}
              </span>
            </label>
          </div>}
        {this.state.showFilters &&
          <div className="livequestions__filter--open">
            <div className="checkbox-btn">
              <label
                htmlFor="markedCheck"
                className="checkbox-btn__label--light"
                aria-label={ariaDisplayOnlyMarked}
                title={ariaDisplayOnlyMarked}
              >
                <input
                  className="checkbox-btn__input"
                  type="checkbox"
                  id="markedCheck"
                  name="markedCheck"
                  checked={this.props.displayOnShortlist}
                  onChange={this.props.toggleDisplayOnShortlist} // eslint-disable-line react/jsx-handler-names
                />
                <span className="checkbox-btn__text">
                  <i className="icon-in-list" aria-hidden="true" />
                </span>
              </label>
            </div>
            <div className="checkbox-btn">
              <label
                htmlFor="displayNotHiddenOnly"
                className="checkbox-btn__label--light pl-3"
                aria-label={ariaDisplayNotHidden}
                title={ariaDisplayNotHidden}
              >
                <input
                  className="checkbox-btn__input"
                  type="checkbox"
                  id="displayNotHiddenOnly"
                  name="displayNotHiddenOnly"
                  checked={this.props.displayNotHiddenOnly}
                  onChange={this.props.toggledisplayNotHiddenOnly} // eslint-disable-line react/jsx-handler-names
                />
                <span className="checkbox-btn__text">
                  <i className="far fa-eye" aria-hidden="true" />
                </span>
              </label>
            </div>
            <div className="checkbox-btn">
              <label
                htmlFor="orderedByLikes"
                className="checkbox-btn__label--light pl-3"
                aria-label={ariaOrderLikes}
                title={ariaOrderLikes}
              >
                <input
                  className="checkbox-btn__input"
                  type="checkbox"
                  id="orderedByLikes"
                  name="orderedByLikes"
                  checked={this.props.orderedByLikes}
                  onChange={this.props.toggleOrdering} // eslint-disable-line react/jsx-handler-names
                />
                <span className="checkbox-btn__text">
                  <i className="fa fa-chevron-up" aria-hidden="true" /> likes
                </span>
              </label>
            </div>
          </div>}
      </div>
    )
  }
}
