export function normalizePromptPayload(formData) {
  return {
    title: formData.title.trim(),
    content: formData.content.trim(),
    description: formData.description?.trim() || null,
    collection_id: formData.collection_id || null,
  }
}

export function toUserMessage(error) {
  const message = error?.message || ''
  const normalized = message.toLowerCase()

  if (normalized.includes('404')) {
    return 'The requested item could not be found.'
  }

  return 'The server is having trouble right now. Please try again shortly.'
}
