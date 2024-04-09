import React from 'react'
import django from 'django'

import Api from '../api'
import { RatingBox } from 'adhocracy4/adhocracy4/ratings/static/ratings/react_ratings'
import api from 'adhocracy4/adhocracy4/static/api'

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
        alert('An error occurred. Please try again: ', error.JSONResponse.message)
        console.log('Error Details:', error)
      })
  }

  handleRatingModify (number, id) {
    const oldValue = this.state.userRating
    console.log(this.props.objectId)

    // super.handleRatingModify(number, id)
    api.rating.change({
      urlReplaces: {
        objectPk: this.props.objectId,
        contentTypeId: this.props.contentType
      },
      value: number
    }, id)
      .done(function (data) {
        this.setState({
          positiveRatings: data.meta_info.positive_ratings_on_same_object,
          negativeRatings: data.meta_info.negative_ratings_on_same_object,
          userRating: data.meta_info.user_rating_on_same_object_value
        })
      }.bind(this))

    Api.rating.change({
      oldValue,
      newValue: number,
      ideaId: this.props.objectId
    })
      .then((response) => {
        console.log('Success:', response)
      })
      .catch((error) => {
        alert('An error occurred. Please try again.' + error.responseJSON.message)
        console.log('Error Details:', error.responseJSON.message)
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
          name="upvote"
          aria-label={translations.upvote}
          className={getRatingClasses('up')}
          style={this.state.userRating && this.props.ideaStatus === 'ACCEPTED' ? { color: '#A0A0FF' } : {}}
          disabled={this.props.ideaStatus === 'ACCEPTED'}
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
