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
      return _sendRequest(baseURL + 'add_choins_sum/', 'POST', data)
    },
    change: function (data) {
      return _sendRequest(baseURL + 'update_choins_sum/', 'POST', data)
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
