import { apiRequest } from './client'

export async function getCollections() {
  const data = await apiRequest('/collections')
  return data?.collections || []
}

export function createCollection(payload) {
  return apiRequest('/collections', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function deleteCollection(id) {
  return apiRequest(`/collections/${id}`, {
    method: 'DELETE',
  })
}
