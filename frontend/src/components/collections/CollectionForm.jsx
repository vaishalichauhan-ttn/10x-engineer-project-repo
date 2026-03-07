import { useId, useState } from 'react'

import Button from '../shared/Button'
import styles from './CollectionForm.module.css'

function CollectionForm({
  onSubmit,
  existingNames = [],
  isSubmitting = false,
  submitError = '',
}) {
  const [name, setName] = useState('')
  const [fieldError, setFieldError] = useState('')
  const fieldErrorId = useId()
  const submitErrorId = useId()

  function validate(value) {
    const trimmedName = value.trim()
    if (!trimmedName) {
      return 'Please enter a collection name.'
    }
    if (trimmedName.length > 60) {
      return 'Collection name must be 60 characters or fewer.'
    }

    const duplicate = existingNames.some(
      (collectionName) => collectionName.trim().toLowerCase() === trimmedName.toLowerCase(),
    )
    if (duplicate) {
      return 'Collection names must be unique.'
    }

    return ''
  }

  async function handleSubmit(event) {
    event.preventDefault()
    const validationError = validate(name)
    setFieldError(validationError)
    if (validationError) {
      return
    }

    const wasSaved = await onSubmit({ name: name.trim() })
    if (wasSaved) {
      setName('')
      setFieldError('')
    }
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <input
        value={name}
        onChange={(event) => {
          setName(event.target.value)
          if (fieldError) {
            setFieldError('')
          }
        }}
        placeholder="Collection name"
        aria-label="Collection name"
        maxLength={60}
        aria-invalid={Boolean(fieldError)}
        aria-describedby={[
          fieldError ? fieldErrorId : '',
          submitError ? submitErrorId : '',
        ]
          .filter(Boolean)
          .join(' ')}
        disabled={isSubmitting}
      />
      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Adding...' : 'Add'}
      </Button>
      {fieldError && (
        <p id={fieldErrorId} className={styles.fieldError} role="alert">
          {fieldError}
        </p>
      )}
      {submitError && (
        <p id={submitErrorId} className={styles.submitError} role="alert">
          {submitError}
        </p>
      )}
    </form>
  )
}

export default CollectionForm
