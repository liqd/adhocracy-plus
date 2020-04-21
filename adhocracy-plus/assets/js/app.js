import 'bootstrap' // load bootstrap components
import 'django'
import 'slick-carousel' // for project timeline

import './unload_warning.js'
import '../../../apps/actions/assets/timestamps.js'
import '../../../apps/dashboard/assets/ajax_modal.js'
import '../../../apps/maps/assets/map-address.js'
import '../../../apps/moderatorremark/assets/idea_remarks.js'
import '../../../apps/newsletters/assets/dynamic_fields.js'

// expose react components
import {
  comments as ReactComments,
  comments_async as ReactCommentsAsync,
  ratings as ReactRatings,
  reports as ReactReports,
  follows as ReactFollows,
  widget as ReactWidget
} from 'adhocracy4'

import * as ReactDocuments from '../../../apps/documents/assets/react_documents.jsx'
import * as ReactPolls from '../../../apps/polls/assets/react_polls.jsx'
import * as ReactQuestions from '../../../apps/questions/assets/react_questions.jsx'
import * as ReactQuestionsPresent from '../../../apps/questions/assets/react_questions_present.jsx'

function init () {
  ReactWidget.initialise('a4', 'comment', ReactComments.renderComment)
  ReactWidget.initialise('a4', 'comment_async', ReactCommentsAsync.renderComment)
  ReactWidget.initialise('a4', 'follows', ReactFollows.renderFollow)
  ReactWidget.initialise('a4', 'ratings', ReactRatings.renderRatings)
  ReactWidget.initialise('a4', 'reports', ReactReports.renderReports)

  ReactWidget.initialise('mb', 'document-management', ReactDocuments.renderDocumentManagement)
  ReactWidget.initialise('mb', 'polls', ReactPolls.renderPolls)
  ReactWidget.initialise('mb', 'poll-management', ReactPolls.renderPollManagement)

  ReactWidget.initialise('speakup', 'questions', ReactQuestions.renderQuestions)
  ReactWidget.initialise('speakup', 'present', ReactQuestionsPresent.renderData)

  $('.timeline-carousel__item').slick({
    initialSlide: parseInt($('#timeline-carousel').attr('data-initial-slide')),
    focusOnSelect: false,
    centerMode: true,
    dots: false,
    arrows: true,
    centerPadding: 30,
    mobileFirst: true,
    infinite: false,
    variableWidth: true,
    slidesToShow: 1,
    slidesToScroll: 1
  })
}

document.addEventListener('DOMContentLoaded', init, false)
document.addEventListener('a4.embed.ready', init, false)

// Closes bootstrap collapse on click elsewhere
$(document).on('click', function () {
  $('.collapse').collapse('hide')
})

// enables bootstrap tooltips
$(function tooltip () {
  $('[data-toggle="tooltip"]').tooltip()
})

// This function is overwritten with custom behavior in embed.js.
export function getCurrentPath () {
  return location.pathname
}
