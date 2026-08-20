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
    try {
      const data: T = await response.json()
      return [data, undefined]
    } catch (error) {
      return [undefined, error]
    }
  }
}

export default api
