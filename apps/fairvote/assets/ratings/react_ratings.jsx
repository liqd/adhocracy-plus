import React from 'react'
import django from 'django'

import Api from '../api'
import { RatingBox } from 'adhocracy4/adhocracy4/ratings/static/ratings/react_ratings'
import api from 'adhocracy4/adhocracy4/static/api'
import './vote.css'
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
        Api.rating.change({
          oldValue,
          newValue: number,
          positiveRatings: data.meta_info.positive_ratings_on_same_object,
          ideaId: this.props.objectId
        })
          .then((response) => {
            console.log('Success:', response)
          })
          .catch((error) => {
            alert('An error occurred. Please try again.' + error.responseJSON.message)
            console.log('Error Details:', error.responseJSON.message)
          })
      }.bind(this))
  }

  render () {
    const getRatingClasses = () => {
      const cssClasses = this.state.userRating === 1
        ? 'fa-solid fa-thumbs-up fa-xl vote'
        : 'fa-regular fa-thumbs-up fa-xl vote'
      return cssClasses
    }
    const isDisabled = () => {
      console.log(this.props.isReadOnly)
      return this.props.ideaStatus === 'ACCEPTED' || this.props.isReadOnly
    }

    return (
      <div className="vote-container">
        <div>
          <button
            name="upvote"
            className="icon rating-button"
            aria-label={translations.upvote}
            disabled={isDisabled()}
            onClick={this.ratingUp.bind(this)}
          >
            <i className={getRatingClasses()} aria-hidden="true" />
          </button>
        </div>
        <div>
          {this.state.positiveRatings}
        </div>
      </div>
    )
  }
}
