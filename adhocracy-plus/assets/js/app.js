import 'bootstrap' // load bootstrap components
import 'django'
import 'select2' // used to skin select element used in livequestions
import 'slick-carousel' // for project timeline

import '../../../apps/actions/assets/timestamps.js'
import '../../../apps/dashboard/assets/ajax_modal.js'
import '../../../apps/maps/assets/map-address.js'
import '../../../apps/moderatorremark/assets/idea_remarks.js'
import '../../../apps/newsletters/assets/dynamic_fields.js'
import '../../../apps/mapideas/assets/js/map_list_view.js'

// expose react components
import {
  commentsAsync as ReactCommentsAsync,
  follows as ReactFollows,
  ratings as ReactRatings,
  reports as ReactReports,
  widget as ReactWidget
} from 'adhocracy4'

import { renderLanguageChoice } from '../../../apps/organisations/assets/react_language_choice.jsx'

function init () {
  ReactWidget.initialise('a4', 'comment_async', ReactCommentsAsync.renderComment)
  ReactWidget.initialise('a4', 'follows', ReactFollows.renderFollow)
  ReactWidget.initialise('a4', 'ratings', ReactRatings.renderRatings)
  ReactWidget.initialise('a4', 'reports', ReactReports.renderReports)

  ReactWidget.initialise('euth', 'language-choice', renderLanguageChoice)

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

  $('.project-tile-carousel').slick({
    initialSlide: 0,
    focusOnSelect: false,
    centerMode: false,
    dots: false,
    arrows: false,
    centerPadding: 30,
    mobileFirst: true,
    infinite: false,
    variableWidth: false,
    slidesToShow: 1.2,
    responsive: [
      {
        breakpoint: 1024,
        settings: {
          slidesToShow: 3,
          arrows: true
        }
      }
    ]
  })

  if ($.fn.select2) {
    $('.js-select2').select2()
  }
}

document.addEventListener('DOMContentLoaded', init, false)
document.addEventListener('DOMContentLoaded', function () {
  // Add toggle buttons to password fields
  document.querySelectorAll('.password-toggle').forEach(function (passwordField) {
    // Create wrapper
    const wrapper = document.createElement('div')
    wrapper.className = 'password-field-wrapper'

    // Wrap the password field
    passwordField.parentNode.insertBefore(wrapper, passwordField)
    wrapper.appendChild(passwordField)

    // Create toggle button
    const toggleBtn = document.createElement('button')
    toggleBtn.type = 'button'
    toggleBtn.className = 'password-toggle-btn'
    toggleBtn.innerHTML = '<i class="fas fa-eye"></i>'
    toggleBtn.setAttribute('aria-label', 'Show password')

    // Add toggle functionality
    toggleBtn.addEventListener('click', function () {
      const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password'
      passwordField.setAttribute('type', type)

      // Update button icon and aria-label
      if (type === 'text') {
        this.innerHTML = '<i class="fas fa-eye-slash"></i>'
        this.setAttribute('aria-label', 'Hide password')
      } else {
        this.innerHTML = '<i class="fas fa-eye"></i>'
        this.setAttribute('aria-label', 'Show password')
      }
    })

    wrapper.appendChild(toggleBtn)
  })
})
export function getCurrentPath () {
  return location.pathname
}
