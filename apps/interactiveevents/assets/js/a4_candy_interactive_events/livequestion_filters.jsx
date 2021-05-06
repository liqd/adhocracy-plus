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
    const allTag = django.gettext('all')
    const onlyShowMarkedText = django.gettext('only show marked questions')
    const displayNotHiddenText = django.gettext('display only questions which are not hidden')
    const orderLikesText = django.gettext('order by likes')
    return (
      <div className="livequestions__filter">
        <div className={'dropdown livequestions__filter--btn ' + (this.state.showFilters && 'mb-5')}>
          <button
            className={this.getButtonClass()} type="button" id="dropdownMenuButton"
            data-toggle="dropdown" aria-haspopup="true" aria-expanded="false"
          >
            {this.props.currentCategoryName}
            <i className="fa fa-caret-down" aria-hidden="true" />
          </button>
          <div className="dropdown-menu" aria-labelledby="dropdownMenuButton">
            <button className="dropdown-item" data-value={-1} onClick={this.selectCategory.bind(this)} href="#">{allTag}</button>
            {this.props.categories.map((category, index) => {
              return <button className="dropdown-item" key={index} data-value={category} onClick={this.selectCategory.bind(this)} href="#">{category}</button>
            })}
          </div>
        </div>
        {this.props.isModerator &&
          <div className="checkbox-btn livequestions__filter--btn pr-3">
            <label htmlFor="markedCheck" className="checkbox-btn__label--light">
              <input
                className="checkbox-btn__input"
                type="checkbox"
                id="markedCheck"
                name="markedCheck"
                checked={this.props.showFilters}
                onChange={this.handleToggleFilters.bind(this)} // eslint-disable-line react/jsx-handler-names
              />
              <span className="checkbox-btn__text">
                <i className="fas fa-sliders-h" aria-label={onlyShowMarkedText} />
                {textFilters}
              </span>
            </label>
          </div>}
        {this.state.showFilters &&
          <div className="livequestions__filter--open">
            <div className="checkbox-btn">
              <label htmlFor="markedCheck" className="checkbox-btn__label--light">
                <input
                  className="checkbox-btn__input"
                  type="checkbox"
                  id="markedCheck"
                  name="markedCheck"
                  checked={this.props.displayOnShortlist}
                  onChange={this.props.toggleDisplayOnShortlist} // eslint-disable-line react/jsx-handler-names
                />
                <span className="checkbox-btn__text">
                  <i className="icon-in-list" aria-label={onlyShowMarkedText} />
                </span>
              </label>
            </div>
            <div className="checkbox-btn">
              <label htmlFor="displayNotHiddenOnly" className="checkbox-btn__label--light pl-3">
                <input
                  className="checkbox-btn__input"
                  type="checkbox"
                  id="displayNotHiddenOnly"
                  name="displayNotHiddenOnly"
                  checked={this.props.displayNotHiddenOnly}
                  onChange={this.props.toggledisplayNotHiddenOnly} // eslint-disable-line react/jsx-handler-names
                />
                <span className="checkbox-btn__text">
                  <i className="far fa-eye" aria-label={displayNotHiddenText} />
                </span>
              </label>
            </div>
            <div className="checkbox-btn">
              <label htmlFor="orderedByLikes" className="checkbox-btn__label--light pl-3">
                <input
                  className="checkbox-btn__input"
                  type="checkbox"
                  id="orderedByLikes"
                  name="orderedByLikes"
                  checked={this.props.orderedByLikes}
                  onChange={this.props.toggleOrdering} // eslint-disable-line react/jsx-handler-names
                />
                <span className="checkbox-btn__text">
                  <i className="fa fa-chevron-up" aria-label={orderLikesText} /> likes
                </span>
              </label>
            </div>
          </div>}
      </div>
    )
  }
}
