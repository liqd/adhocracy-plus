import 'bootstrap' // load bootstrap components
import 'django'
import 'select2' // used to skin select element used in livequestions
import 'slick-carousel' // for project timeline

import '../../../apps/actions/assets/timestamps.js'
import '../../../apps/dashboard/assets/ajax_modal.js'
import '../../../apps/maps/assets/map-address.js'
import '../../../apps/moderatorremark/assets/idea_remarks.js'
import '../../../apps/newsletters/assets/dynamic_fields.js'

// expose react components
import {
  comments as ReactComments,
  commentsAsync as ReactCommentsAsync,
  ratings as ReactRatings,
  reports as ReactReports,
  follows as ReactFollows,
  widget as ReactWidget
} from 'adhocracy4'

import * as ReactDocuments from '../../../apps/documents/assets/react_documents.jsx'
import * as ReactPolls from '../../../apps/polls/assets/react_polls.jsx'
import * as ReactInteractiveEvents from 'a4_candy_interactive_events'
import * as ReactLanguageChoice from '../../../apps/organisations/assets/react_language_choice.jsx'

function init () {
  ReactWidget.initialise('a4', 'comment', ReactComments.renderComment)
  ReactWidget.initialise('a4', 'comment_async', ReactCommentsAsync.renderComment)
  ReactWidget.initialise('a4', 'follows', ReactFollows.renderFollow)
  ReactWidget.initialise('a4', 'ratings', ReactRatings.renderRatings)
  ReactWidget.initialise('a4', 'reports', ReactReports.renderReports)

  ReactWidget.initialise('mb', 'document-management', ReactDocuments.renderDocumentManagement)
  ReactWidget.initialise('mb', 'polls', ReactPolls.renderPolls)
  ReactWidget.initialise('mb', 'poll-management', ReactPolls.renderPollManagement)

  ReactWidget.initialise('aplus', 'questions', ReactInteractiveEvents.renderLiveQuestions)
  ReactWidget.initialise('aplus', 'present', ReactInteractiveEvents.renderLiveQuestionsPresent)

  ReactWidget.initialise('euth', 'language-choice', ReactLanguageChoice.renderLanguageChoice)

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

  if ($.fn.select2) {
    $('.js-select2').select2()
  }

  // This function adds required classes to iframes added by ckeditor
  $('.rich-text iframe').addClass('ck_embed_iframe')
  $('.ck_embed_iframe').parent('div').addClass('ck_embed_iframe__container')
}

document.addEventListener('DOMContentLoaded', init, false)
document.addEventListener('a4.embed.ready', init, false)

// Closes selected collapsable elements on click elsewhere - still not sure if we need this?!
document.addEventListener('click', function () {
  $('.js-selector-collapse').collapse('hide')
})

// enables bootstrap tooltips
$(function tooltip () {
  $('[data-toggle="tooltip"]').tooltip()
})

// This function is overwritten with custom behavior in embed.js.
export function getCurrentPath () {
  return location.pathname
}
