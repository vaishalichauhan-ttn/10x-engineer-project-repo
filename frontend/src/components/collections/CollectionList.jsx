import Button from '../shared/Button'
import styles from './CollectionList.module.css'

function CollectionList({ collections, onRequestDeleteCollection }) {
  if (collections.length === 0) {
    return (
      <p className={styles.empty} role="status" aria-live="polite">
        No collections created yet. Add one above to organize your prompts.
      </p>
    )
  }

  return (
    <ul className={styles.list}>
      {collections.map((collection) => (
        <li key={collection.id} className={styles.item}>
          <span>{collection.name}</span>
          <Button variant="danger" onClick={() => onRequestDeleteCollection(collection)}>
            Delete
          </Button>
        </li>
      ))}
    </ul>
  )
}

export default CollectionList
