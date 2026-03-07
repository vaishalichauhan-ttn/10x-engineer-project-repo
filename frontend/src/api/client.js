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

function buildErrorMessage(payload, status) {
  if (!payload) {
    return `Request failed with status ${status}`
  }

  if (Array.isArray(payload.detail)) {
    return payload.detail.map((item) => item.msg).join(', ')
  }

  return payload.detail || `Request failed with status ${status}`
}

export async function apiRequest(path, options = {}) {
  let response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
      ...options,
    })
  } catch {
    throw new Error('Network error. Please check your connection and try again.')
  }

  const payload = await parseJson(response)

  if (!response.ok) {
    throw new Error(buildErrorMessage(payload, response.status))
  }

  return payload
}
