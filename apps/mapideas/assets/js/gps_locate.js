/* global django */

const GEOLOCATION_TIMEOUT = 10000

function getLines (array) {
  const output = []
  if (array.length) {
    if ('lat' in array[0]) {
      for (let i = 0, j = array.length - 1; i < array.length; j = i++) {
        output.push([array[i], array[j]])
      }
    } else {
      array.forEach(function (a) {
        getLines(a).forEach(function (line) {
          output.push(line)
        })
      })
    }
  }
  return output
}

function isPointInsidePolygon (latlng, polygonLayer) {
  const x = latlng.lat
  const y = latlng.lng

  // Algorithm comes from:
  // https://github.com/substack/point-in-polygon/blob/master/index.js
  let inside = false

  getLines(polygonLayer.getLatLngs()).forEach(function (line) {
    const xi = line[0].lat
    const yi = line[0].lng
    const xj = line[1].lat
    const yj = line[1].lng

    //      *
    //     /
    // *--/----------->>
    //   *
    // Check that
    //
    // 1.  yi and yj are on opposite sites of a ray to the right
    // 2.  the intersection of the ray and the segment is right of x
    const intersect = ((yi > y) !== (yj > y)) &&
        (x < (xj - xi) * (y - yi) / (yj - yi) + xi)
    if (intersect) inside = !inside
  })
  return inside
}

function isPointInsideGeoJson (latlng, geojson) {
  if (!geojson) {
    return true
  }

  const polygon = window.L.geoJSON(geojson)
  const layers = polygon.getLayers()

  // No restriction polygon configured: allow every location.
  if (!layers.length) {
    return true
  }

  return layers.some(function (layer) {
    return isPointInsidePolygon(latlng, layer)
  })
}

function getGeoJsonForLatLng (latlng) {
  return {
    type: 'Feature',
    properties: {
      strasse: '',
      haus: '',
      plz: '',
      ortsteil: ''
    },
    geometry: {
      type: 'Point',
      coordinates: [latlng.lng, latlng.lat]
    }
  }
}

function setStatus (button, message) {
  const status = button.parentElement.querySelector('[data-gps-locate-status]')
  if (!status) {
    return
  }
  status.textContent = message
  status.hidden = !message
}

function locate (mapElement, button) {
  if (!('geolocation' in navigator)) {
    setStatus(button, django.gettext('Geolocation is not supported by your browser.'))
    return
  }

  const name = mapElement.getAttribute('data-name')
  const input = document.getElementById('id_' + name)
  if (!input) {
    return
  }

  let polygon = null
  try {
    polygon = JSON.parse(mapElement.getAttribute('data-polygon'))
  } catch {
    polygon = null
  }

  button.disabled = true
  setStatus(button, django.gettext('Locating...'))

  navigator.geolocation.getCurrentPosition(
    function (position) {
      button.disabled = false

      const latlng = {
        lat: position.coords.latitude,
        lng: position.coords.longitude
      }

      if (!isPointInsideGeoJson(latlng, polygon)) {
        setStatus(button, django.gettext('Your current location is outside the marked area.'))
        return
      }

      input.value = JSON.stringify(getGeoJsonForLatLng(latlng))
      input.dispatchEvent(new Event('change', { bubbles: true }))
      setStatus(button, '')
    },
    function (error) {
      button.disabled = false
      let message = django.gettext('Could not determine your location.')
      if (error.code === error.PERMISSION_DENIED) {
        message = django.gettext('Location access was denied. Please enable location services and try again.')
      }
      setStatus(button, message)
    },
    {
      enableHighAccuracy: true,
      timeout: GEOLOCATION_TIMEOUT,
      maximumAge: 30000
    }
  )
}

function init () {
  document.querySelectorAll('[data-gps-locate]').forEach(function (button) {
    if (button.dataset.gpsInitialized) {
      return
    }
    button.dataset.gpsInitialized = 'true'

    const form = button.closest('form')
    const mapElement = form
      ? form.querySelector('[data-map="choose_point"]')
      : document.querySelector('[data-map="choose_point"]')

    if (!mapElement) {
      return
    }

    button.addEventListener('click', function () {
      locate(mapElement, button)
    })
  })
}

function boot () {
  init()
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', boot, false)
} else {
  boot()
}
document.addEventListener('a4.embed.ready', boot, false)
