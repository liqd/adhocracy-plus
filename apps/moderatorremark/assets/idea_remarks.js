import * as bootstrap from 'bootstrap'
const $ = require('jquery')
const a4api = require('adhocracy4').api

/* eslint-disable */
$(function () {
  const dropdown = $('#idea-remark__dropdown')
  const attributes = dropdown.data('attributes')
  if (typeof attributes !== 'undefined') {
    var objectPk = attributes.item_object_id
    var contentTypeId = attributes.item_content_type
    var remarkId = attributes.id
    var remarkVal = attributes.remark
  }

  if (remarkId) {
    $('#id_remark').val(remarkVal)
  }

  $('#idea-remark__form').submit(function (e) {
    e.preventDefault()
    const $input = $('#id_remark')
    const newVal = $input.val()
    const buttonSelector = 'button#idea-remark__dropdown.dropdown-toggle.show'

    if (remarkVal !== newVal) {
      const data = {
        urlReplaces: {
          objectPk: objectPk,
          contentTypeId: contentTypeId
        },
        remark: newVal
      }

      let response
      if (remarkId) {
        response = a4api.moderatorremark.change(data, remarkId)
      } else {
        response = a4api.moderatorremark.add(data)
      }


      response.done(remark => {
        remarkId = remark.id
        remarkVal = remark.remark
        const tickSymbol = document.querySelector('.idea-remark__btn__notify')
        if (remarkVal) {
          tickSymbol.classList.remove('d-none')
        } else {
          tickSymbol.classList.add('d-none')
        }
        const remarkButton = document.querySelector(buttonSelector)
        const remarkDropdown = new bootstrap.Dropdown(remarkButton)
        remarkDropdown.hide()
      })
    } else {
      const remarkButton = document.querySelector(buttonSelector)
      const remarkDropdown = new bootstrap.Dropdown(remarkButton)
      remarkDropdown.hide()
    }
  })
})
/* eslint-enable */
