import { useState } from 'react'

import Button from '../shared/Button'
import styles from './CollectionForm.module.css'

function CollectionForm({ onSubmit }) {
  const [name, setName] = useState('')

  function handleSubmit(event) {
    event.preventDefault()
    const trimmedName = name.trim()
    if (!trimmedName) {
      return
    }

    onSubmit({ name: trimmedName })
    setName('')
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <input
        value={name}
        onChange={(event) => setName(event.target.value)}
        placeholder="Collection name"
        aria-label="Collection name"
      />
      <Button type="submit">Add</Button>
    </form>
  )
}

export default CollectionForm
