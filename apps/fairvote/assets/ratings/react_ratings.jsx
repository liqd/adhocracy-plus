import React from 'react'
import django from 'django'

import Api from '../../static/api'
import { RatingBox } from 'adhocracy4/adhocracy4/ratings/static/ratings/react_ratings'
const translations = {
  upvote: django.gettext('vote')
}

export default class RatingChoinsBox extends RatingBox {
  handleRatingCreate (number) {
    super.handleRatingCreate(number)
    console.log(this.props.objectId)
    Api.rating.add({
      value: number,
      ideaId: this.props.objectId
    })
      .then((response) => {
        console.log('Success:', response)
      })
      .catch((error) => {
        alert('An error occurred. Please try again.')
        console.log('Error Details:', error)
      })
  }

  handleRatingModify (number, id) {
    const oldValue = this.state.userRating
    console.log(this.props.objectId)

    super.handleRatingModify(number, id)
    Api.rating.change({
      oldValue,
      newValue: number,
      ideaId: this.props.objectId
    })
      .then((response) => {
        console.log('Success:', response)
      })
      .catch((error) => {
        alert('An error occurred. Please try again.')
        console.log('Error Details:', error)
      })
  }

  render () {
    const getRatingClasses = ratingType => {
      const valueForRatingType = ratingType === 'up' ? 1 : -1
      const cssClasses = this.state.userRating === valueForRatingType
        ? 'rating-button rating-' + ratingType + ' is-selected'
        : 'rating-button rating-' + ratingType
      return cssClasses
    }

    return (
      <div className="rating">
        <button
          aria-label={translations.upvote}
          className={getRatingClasses('up')}
          disabled={this.props.isReadOnly}
          onClick={this.ratingUp.bind(this)}
        >
          <i className="fa fa-chevron-up" aria-hidden="true" />
          {translations.upvote}
        </button>
        <i className="fas fa-user" aria-hidden="true" />
        {this.state.positiveRatings}
      </div>
    )
  }
}
