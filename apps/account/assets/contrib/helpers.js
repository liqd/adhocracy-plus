import cookie from 'js-cookie'
import django from 'django'

export function updateItem (data, url, method) {
  return fetch(url, {
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'X-CSRFToken': cookie.get('csrftoken')
    },
    method,
    body: JSON.stringify(data)
  }
  )
}

// toLocaleDate returns a formatted and internationalized
// date string. Fallback formatting is the German variant.
// input: 2021-11-11T15:37:19.490201+01:00
// output: 11. November 2021 (depending on locale)
export const toLocaleDate = (
  isodate,
  locale = 'de-DE',
  formatStyle = { month: 'short', day: 'numeric', year: 'numeric' }
) => {
  const date = new Date(isodate)
  return new Intl.DateTimeFormat(locale, formatStyle).format(date)
}

/*
 * checks if two arrays are equal
 *
 * @param {array} a
 * @param {array} b
 * @returns {boolean}
 */
export const arraysEqual = (a, b) => {
  if (a === b) return true
  if (a == null || b == null) return false
  if (a.length !== b.length) return false

  const aSorted = [...a].sort()
  const bSorted = [...b].sort()

  for (let i = 0; i < aSorted.length; ++i) {
    if (aSorted[i] !== bSorted[i]) return false
  }
  return true
}

/*
 * converts an object to URLSearchParams
 *
 * This function takes an object and converts it into a URLSearchParams
 * instance, which can be used for query string formatting in URLs.
 * It handles arrays by appending each value to the parameter, and ignores
 * any null or undefined values.
 *
 * Example:
 * For the input:
 *   { search: 'apple', category: 'fruit', tags: ['red', 'green'], page: null }
 * The output will be:
 *   "search=apple&category=fruit&tags=red&tags=green"
 *
 * @param {Object} params - The object to convert into URLSearchParams
 * @returns {URLSearchParams} - The resulting URLSearchParams instance
 */
export const toSearchParams = (params) => {
  return Object.entries(params).reduce((acc, [key, value]) => {
    if (value == null || value === '') return acc

    if (Array.isArray(value)) {
      value.forEach(val => (val != null && val !== '') && acc.append(key, val))
    } else {
      acc.set(key, value)
    }

    return acc
  }, new URLSearchParams())
}

/*
 * Calculates the geographical distance between two points using the Haversine formula.
 *
 * This function computes the shortest distance between two latitude/longitude coordinates
 * on Earth's surface, returning the result in meters.
 *
 * Example:
 * getDistanceBetweenPoints([13.405, 52.52], [9.9937, 53.5511])
 * returns: ~255600 meters (distance between Berlin and Hamburg)
 *
 * @param {number[]} coords1 - [longitude, latitude] of the first point
 * @param {number[]} coords2 - [longitude, latitude] of the second point
 * @returns {number} - Distance between the two points in meters
 */
export const getDistanceBetweenPoints = (coords1, coords2) => {
  const toRad = (angle) => (angle * Math.PI) / 180

  const [lon1, lat1] = coords1
  const [lon2, lat2] = coords2

  const earthRadiusInMeters = 6371000
  const deltaLat = toRad(lat2 - lat1)
  const deltaLon = toRad(lon2 - lon1)

  const haversineFormula =
    Math.sin(deltaLat / 2) * Math.sin(deltaLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(deltaLon / 2) * Math.sin(deltaLon / 2)

  const centralAngle = 2 * Math.atan2(Math.sqrt(haversineFormula), Math.sqrt(1 - haversineFormula))

  return earthRadiusInMeters * centralAngle
}

const statusNames = [django.gettext('ongoing'), django.gettext('upcoming'), django.gettext('done')]
const plansText = django.gettext('Plans')

/*
 * Converts a search profile object into a structured list of filters.
 *
 * This function extracts relevant filtering criteria from a given search profile
 * and returns them as an array of arrays, where each sub-array represents a different
 * filter category. Empty filters are removed to ensure a clean output.
 *
 * Example:
 * Given a search profile:
 * {
 *   query_text: "Lichtenberg",
 *   districts: [{ name: "Charlottenburg-Wilmersdorf" }, { name: "Friedrichshain-Kreuzberg" }],
 *   topics: [{ name: "Work & economy" }],
 *   project_types: [{ name: "information (no participation)" }],
 *   status: [{ name: "ongoing" }],
 *   organisations: [{ name: "liqd" }],
 *   kiezradars: [{ name: "Kiezradar 1" }],
 *   plans_only: true
 * }
 *
 * The output will be:
 * [
 *   ["Lichtenberg"],
 *   ["Charlottenburg-Wilmersdorf", "Friedrichshain-Kreuzberg"],
 *   ["Work & economy"],
 *   ["information (no participation)"],
 *   ["ongoing"],
 *   ["liqd"],
 *   ["Kiezradar 1"],
 *   ["Plans"]
 * ]
 *
 * @param {Object} searchProfile - The search profile containing filter criteria
 * @returns {string[][]} - A structured list of filter values
 */
export const toFilterList = (searchProfile) => {
  const filters = [
    searchProfile.districts,
    searchProfile.topics,
    searchProfile.project_types,
    searchProfile.status.map((status) => ({ name: statusNames[status.status] })),
    searchProfile.organisations,
    searchProfile.kiezradars
  ].map((filter) => filter.map(({ name }) => name))

  return [
    [searchProfile.query_text],
    ...filters,
    [searchProfile.plans_only ? plansText : null]
  ].filter(arr => arr.some(value => value))
}
