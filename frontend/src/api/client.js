import { API_BASE_URL } from '../config/env'

async function parseJson(response) {
  const text = await response.text()
  if (!text) {
    return null
  }

  try {
    return JSON.parse(text)
  } catch {
    return { detail: text }
  }
}

export async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  })

  const payload = await parseJson(response)

  if (!response.ok) {
    const message = payload?.detail || `Request failed with status ${response.status}`
    throw new Error(message)
  }

  return payload
}
