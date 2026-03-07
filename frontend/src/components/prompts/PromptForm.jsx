import { useState } from 'react'

import Button from '../shared/Button'
import styles from './PromptForm.module.css'

function buildInitialValues(initialData) {
  if (!initialData) {
    return {
      title: '',
      description: '',
      content: '',
      collection_id: '',
    }
  }

  return {
    title: initialData.title || '',
    description: initialData.description || '',
    content: initialData.content || '',
    collection_id: initialData.collection_id || '',
  }
}

function PromptForm({
  initialData = null,
  collections,
  submitLabel = 'Save Prompt',
  onSubmit,
  onCancel,
}) {
  const [formValues, setFormValues] = useState(() => buildInitialValues(initialData))

  function updateField(field, value) {
    setFormValues((current) => ({ ...current, [field]: value }))
  }

  function handleSubmit(event) {
    event.preventDefault()
    onSubmit({
      ...formValues,
      collection_id: formValues.collection_id || null,
    })
  }

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <label>
        Title
        <input
          required
          value={formValues.title}
          onChange={(event) => updateField('title', event.target.value)}
        />
      </label>

      <label>
        Description
        <input
          value={formValues.description}
          onChange={(event) => updateField('description', event.target.value)}
        />
      </label>

      <label>
        Collection
        <select
          value={formValues.collection_id}
          onChange={(event) => updateField('collection_id', event.target.value)}
        >
          <option value="">No collection</option>
          {collections.map((collection) => (
            <option key={collection.id} value={collection.id}>
              {collection.name}
            </option>
          ))}
        </select>
      </label>

      <label>
        Prompt content
        <textarea
          required
          rows={8}
          value={formValues.content}
          onChange={(event) => updateField('content', event.target.value)}
        />
      </label>

      <div className={styles.actions}>
        <Button type="submit">{submitLabel}</Button>
        <Button variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </form>
  )
}

export default PromptForm
