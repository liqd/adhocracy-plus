import cookie from 'js-cookie'

export function updateItem (data: unknown, url: string, method: string) {
  return fetch(url, {
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'X-CSRFToken': cookie.get('csrftoken') || ''
    },
    method,
    body: JSON.stringify(data)
  }
  )
}
