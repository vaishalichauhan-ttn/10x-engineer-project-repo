import { useId, useState } from 'react'

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
  isSubmitting = false,
  submitError = '',
}) {
  const [formValues, setFormValues] = useState(() => buildInitialValues(initialData))
  const [errors, setErrors] = useState({})
  const titleErrorId = useId()
  const contentErrorId = useId()
  const submitErrorId = useId()

  function updateField(field, value) {
    setFormValues((current) => ({ ...current, [field]: value }))
    setErrors((current) => {
      if (!current[field]) {
        return current
      }
      const next = { ...current }
      delete next[field]
      return next
    })
  }

  function validate(values) {
    const nextErrors = {}
    const title = values.title.trim()
    const content = values.content.trim()

    if (!title) {
      nextErrors.title = 'Please add a title.'
    } else if (title.length > 120) {
      nextErrors.title = 'Title must be 120 characters or fewer.'
    }

    if (!content) {
      nextErrors.content = 'Please add prompt content.'
    }

    return nextErrors
  }

  function handleSubmit(event) {
    event.preventDefault()
    const nextErrors = validate(formValues)
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) {
      return
    }

    onSubmit({
      ...formValues,
      title: formValues.title.trim(),
      content: formValues.content.trim(),
      description: formValues.description.trim(),
      collection_id: formValues.collection_id || null,
    })
  }

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <label>
        Title
        <input
          value={formValues.title}
          onChange={(event) => updateField('title', event.target.value)}
          maxLength={120}
          aria-invalid={Boolean(errors.title)}
          aria-describedby={errors.title ? titleErrorId : undefined}
          disabled={isSubmitting}
        />
        {errors.title && (
          <span id={titleErrorId} className={styles.fieldError}>
            {errors.title}
          </span>
        )}
      </label>

      <label>
        Description
        <input
          value={formValues.description}
          onChange={(event) => updateField('description', event.target.value)}
          disabled={isSubmitting}
        />
      </label>

      <label>
        Collection
        <select
          value={formValues.collection_id}
          onChange={(event) => updateField('collection_id', event.target.value)}
          disabled={isSubmitting}
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
          rows={8}
          value={formValues.content}
          onChange={(event) => updateField('content', event.target.value)}
          aria-invalid={Boolean(errors.content)}
          aria-describedby={errors.content ? contentErrorId : undefined}
          disabled={isSubmitting}
        />
        {errors.content && (
          <span id={contentErrorId} className={styles.fieldError}>
            {errors.content}
          </span>
        )}
      </label>

      {submitError && (
        <p id={submitErrorId} className={styles.submitError} role="alert">
          {submitError}
        </p>
      )}

      <div className={styles.actions}>
        <Button type="submit" disabled={isSubmitting} aria-describedby={submitError ? submitErrorId : undefined}>
          {isSubmitting ? 'Saving...' : submitLabel}
        </Button>
        <Button variant="secondary" onClick={onCancel} disabled={isSubmitting}>
          Cancel
        </Button>
      </div>
    </form>
  )
}

export default PromptForm
