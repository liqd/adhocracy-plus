const $ = require('jquery')
const cookie = require('js-cookie')

function init () {
  $.ajaxSetup({
    headers: { 'X-CSRFToken': cookie.get('csrftoken') }
  })
}

document.addEventListener('DOMContentLoaded', init, false)
document.addEventListener('a4.embed.ready', init, false)

const baseURL = '/api/idea-choins/'

const Api = {
  rating: {
    add: function (data) {
      // Rating this idea for the first time
      return _sendRequest(baseURL + 'update_idea_choins_at_user_first_rating/', 'POST', data)
    },
    change: function (data) {
      // Rating this idea that already has ratings
      return _sendRequest(baseURL + 'update_idea_choins_at_user_rating_update/', 'POST', data)
    }
  }
}

function _sendRequest (url, type, data) {
  const $body = $('body')
  const params = {
    url,
    type,
    dataType: 'json',
    data: JSON.stringify(data),
    contentType: 'application/json; charset=utf-8',
    error: function (xhr, status, err) {
      console.error(url, status, err.toString())
    },
    complete: function () {
      $body.removeClass('loading')
    }
  }
  $body.addClass('loading')
  return $.ajax(params)
}

module.exports = Api
