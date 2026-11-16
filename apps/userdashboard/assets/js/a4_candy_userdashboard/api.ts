import Cookies from 'js-cookie'

const DEFAULT_HEADERS: Record<string, string | undefined> = {
  Accept: 'application/json',
  'Content-Type': 'application/json',
  'X-CSRFToken': Cookies.get('csrftoken')
}

interface ApiFetchParams {
  url: string
  method: string
  headers?: Record<string, string | undefined>
  body?: Record<string, unknown>
}

type ApiResult<T> = [T, undefined] | [undefined, unknown]

const api = {
  fetch: async <T = any>({
    url,
    method,
    headers = DEFAULT_HEADERS,
    body
  }: ApiFetchParams): Promise<ApiResult<T>> => {
    const response = await fetch(url, {
      method,
      headers: headers as Record<string, string>,
      body: JSON.stringify(body)
    })
    let data: any
    try {
      data = await response.json()
    } catch {
      data = undefined
    }
    if (!response.ok) {
      const detail = data?.detail ||
        Object.entries(data || {})
          .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
          .join(' ')
      return [undefined, detail || response.statusText]
    }
    return [data as T, undefined]
  }
}

export default api
