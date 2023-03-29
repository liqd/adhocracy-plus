import Cookies from 'js-cookie'

const DEFAULT_HEADERS = {
  Accept: 'application/json',
  'Content-Type': 'application/json',
  'X-CSRFToken': Cookies.get('csrftoken')
}

const api = {
  fetch: async ({
    url,
    method,
    headers = DEFAULT_HEADERS,
    body
  }) => {
    const response = await fetch(url, {
      method,
      headers,
      body: JSON.stringify(body)
    })
    try {
      const data = await response.json()
      return [data, undefined]
    } catch (error) {
      return [undefined, error]
    }
  }
}

export default api
