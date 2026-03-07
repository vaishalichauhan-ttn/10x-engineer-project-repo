import { apiRequest } from './client'

export async function getPrompts() {
  const data = await apiRequest('/prompts')
  return data?.prompts || []
}

export function getPrompt(id) {
  return apiRequest(`/prompts/${id}`)
}

export function createPrompt(payload) {
  return apiRequest('/prompts', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updatePrompt(id, payload) {
  return apiRequest(`/prompts/${id}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export function deletePrompt(id) {
  return apiRequest(`/prompts/${id}`, {
    method: 'DELETE',
  })
}
