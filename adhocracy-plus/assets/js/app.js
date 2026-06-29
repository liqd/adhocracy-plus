import 'bootstrap' // load bootstrap components
import { Dropdown } from 'bootstrap'
import 'django'
import 'select2' // used to skin select element used in livequestions
import 'slick-carousel' // for project tile carousel and polls

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
import { renderProjectDetailFollow } from '../../../apps/projects/assets/js/project_detail_follow.jsx'
import { initGuestProjectAlerts } from '../../../apps/projects/assets/js/guest_project_alert.js'
import { initProjectDetailParticipationView } from '../../../apps/projects/assets/js/project_detail_participation_view.js'
import { initProjectSummary } from '../../../apps/summarization/assets/js/project_summary.js'

function init () {
  ReactWidget.initialise('a4', 'comment_async', ReactCommentsAsync.renderComment)
  ReactWidget.initialise('a4', 'follows', ReactFollows.renderFollow)
  ReactWidget.initialise('a4', 'project-detail-follow', renderProjectDetailFollow)
  ReactWidget.initialise('a4', 'ratings', ReactRatings.renderRatings)
  ReactWidget.initialise('a4', 'reports', ReactReports.renderReports)

  ReactWidget.initialise('euth', 'language-choice', renderLanguageChoice)

  initProjectDetailParticipationView()
  initGuestProjectAlerts()
  initProjectSummary()

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
  document.querySelectorAll('.userindicator__dropdown-close').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const root = btn.closest('.userindicator__dropdown')
      if (!root) {
        return
      }
      const toggle = root.querySelector('.dropdown-toggle.show')
      if (toggle) {
        Dropdown.getOrCreateInstance(toggle).hide()
      }
    })
  })
})
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
