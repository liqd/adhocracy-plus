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

  handleToggleFilters () {
    const newValue = !this.state.showFilters
    this.setState({
      showFilters: newValue
    })
  }

  render () {
    const textFilters = django.gettext(' Filters')
    const ariaOpenFilters = django.gettext('Click to view filters')
    const ariaDisplayOnlyMarked = django.gettext('Click to only display marked questions')
    const ariaDisplayNotHidden = django.gettext('Click to only display questions which are not hidden')
    const ariaOrderLikes = django.gettext('Click to order list by likes')
    const allTag = django.gettext('all')
    const categories = [...this.props.categories]
    categories.unshift(allTag)
    return (
      <div className={'livequestion__filter-bar ' + (this.state.showFilters && 'mb-3')}>
        <div className="dropdown livequestion__filter--btn">
          <button
            className="dropdown-toggle btn btn--select btn--light"
            type="button"
            id="dropdownAffiliationBtn"
            data-bs-toggle="dropdown"
            aria-haspopup="true"
            aria-expanded="false"
          >
            {this.props.currentCategoryName}
            <i className="fa fa-caret-down" aria-hidden="true" />
          </button>
          {this.props.categories.length > 0 &&
            <div className="dropdown-menu" aria-labelledby="dropdownAffiliationBtn">
              {categories.map((category, index) => {
                return (
                  <button
                    className="dropdown-item"
                    key={index}
                    data-value={category === allTag ? -1 : category}
                    onClick={this.selectCategory.bind(this)} href="#"
                  >
                    {category}
                  </button>
                )
              })}
            </div>}
        </div>
        {this.props.isModerator &&
          <div className="checkbox-btn livequestion__filter--btn">
            <label
              htmlFor="showFilters"
              className="checkbox-btn__label--light"
              aria-label={ariaOpenFilters}
              title={ariaOpenFilters}
            >
              <input
                className="checkbox-btn__input"
                type="checkbox"
                id="showFilters"
                name="showFilter"
                checked={this.props.showFilters}
                onChange={this.handleToggleFilters.bind(this)} // eslint-disable-line react/jsx-handler-names
              />
              <span className="checkbox-btn__text--colour">
                <i className="fas fa-sliders-h me-1" aria-hidden="true" />
                {textFilters}
              </span>
            </label>
          </div>}
        {this.state.showFilters &&
          <div className="livequestion__filter--open">
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
                <span className="checkbox-btn__text--colour">
                  <i className="icon-in-list" aria-hidden="true" />
                </span>
              </label>
            </div>
            <div className="checkbox-btn">
              <label
                htmlFor="displayNotHiddenOnly"
                className="checkbox-btn__label--light ps-3"
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
                <span className="checkbox-btn__text--colour">
                  <i className="far fa-eye" aria-hidden="true" />
                </span>
              </label>
            </div>
            <div className="checkbox-btn">
              <label
                htmlFor="orderedByLikes"
                className="checkbox-btn__label--light ps-3"
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
                <span className="checkbox-btn__text--colour">
                  <i className="fa fa-thumbs-up" aria-hidden="true" /> likes
                </span>
              </label>
            </div>
          </div>}
      </div>
    )
  }
}
