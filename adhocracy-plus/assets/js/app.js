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
  comments_async_with_categories as ReactCommentsWithCategories,
  ratings as ReactRatings,
  reports as ReactReports,
  follows as ReactFollows
} from 'adhocracy4'

import * as ReactDocuments from '../../../apps/documents/assets/react_documents.jsx'
import * as ReactPolls from '../../../apps/polls/assets/react_polls.jsx'
import * as ReactQuestions from '../../../apps/questions/assets/react_questions.jsx'
import * as ReactQuestionsPresent from '../../../apps/questions/assets/react_questions_present.jsx'

var initialiseWidget = function (namespace, name, fn) {
  var key = 'data-' + namespace + '-widget'
  var selector = '[' + key + '=' + name + ']'
  $(selector).each(function (i, el) {
    fn(el)

    // avoid double-initialisation
    el.removeAttribute(key)
  })
}

var init = function () {
  initialiseWidget('a4', 'comment', ReactComments.renderComment)
  initialiseWidget('a4', 'comment_async', ReactCommentsAsync.renderComment)
  initialiseWidget('a4', 'comment_async_with_categories', ReactCommentsWithCategories.renderComment)
  initialiseWidget('a4', 'follows', ReactFollows.renderFollow)
  initialiseWidget('a4', 'ratings', ReactRatings.renderRatings)
  initialiseWidget('a4', 'reports', ReactReports.renderReports)

  initialiseWidget('mb', 'document-management', ReactDocuments.renderDocumentManagement)
  initialiseWidget('mb', 'polls', ReactPolls.renderPolls)
  initialiseWidget('mb', 'poll-management', ReactPolls.renderPollManagement)

  initialiseWidget('speakup', 'questions', ReactQuestions.renderQuestions)
  initialiseWidget('speakup', 'present', ReactQuestionsPresent.renderData)

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

$(init)
window.init_widgets = init
$(document).on('a4.embed.ready', init)

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
