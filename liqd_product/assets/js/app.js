/* eslint no-unused-vars: "off", no-new: "off" */

// make jquery available for non-webpack js
var $ = window.jQuery = window.$ = require('jquery')
window.Tether = require('tether/dist/js/tether.js')

// load bootstrap components
require('bootstrap')

// load slick carousel for project timeline
require('slick-carousel')
require('slick-carousel/slick/slick.css')

var django = require('django')

// expose react components
var ReactComments = require('adhocracy4').comments
var ReactRatings = require('adhocracy4').ratings
var ReactReports = require('adhocracy4').reports
var ReactFollows = require('adhocracy4').follows

var ReactDocuments = require('../../../apps/documents/assets/react_documents.jsx')
var ReactPolls = require('../../../apps/polls/assets/react_polls.jsx')

var ReactQuestions = require('../../../apps/questions/assets/react_questions.jsx')
var ReactQuestionsStatistics = require('../../../apps/questions/assets/react_questions_statistics.jsx')
var ReactQuestionsPresent = require('../../../apps/questions/assets/react_questions_present.jsx')

var relativeTimestamps = require('../../../apps/actions/assets/timestamps.js')
var mapAddress = require('./map-address.js')
var remarkpopover = require('../../../apps/moderatorremark/assets/idea_remarks.js')
var dynamicFields = require('../../../apps/contrib/assets/dynamic_fields.js')

// This function is overwritten with custom behavior in embed.js.
var getCurrentPath = function () {
  return location.pathname
}

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
  initialiseWidget('a4', 'follows', ReactFollows.renderFollow)
  initialiseWidget('a4', 'ratings', ReactRatings.renderRatings)
  initialiseWidget('a4', 'reports', ReactReports.renderReports)

  initialiseWidget('mb', 'document-management', ReactDocuments.renderDocumentManagement)
  initialiseWidget('mb', 'polls', ReactPolls.renderPolls)
  initialiseWidget('mb', 'poll-management', ReactPolls.renderPollManagement)

  initialiseWidget('speakup', 'questions', ReactQuestions.renderQuestions)
  initialiseWidget('speakup', 'statistics', ReactQuestionsStatistics.renderData)
  initialiseWidget('speakup', 'present', ReactQuestionsPresent.renderData)
}

$(init)
$(document).on('a4.embed.ready', init)

module.exports = {
  getCurrentPath: getCurrentPath
}

// Closes bootstrap collapse on click elsewhere
$(document).on('click', function () {
  $('.collapse').collapse('hide')
})

// carousel for project timeline
$(document).ready(function () {
  function getInitialSlide () {
    return parseInt($('#timeline-carousel').attr('data-initial-slide'))
  }

  $('.timeline-carousel__item').slick({
    initialSlide: getInitialSlide(),
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
})
