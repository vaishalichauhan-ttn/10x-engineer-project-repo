import Button from '../shared/Button'
import styles from './PromptCard.module.css'

function PromptCard({ prompt, collectionName, onView, onEdit, onDelete }) {
  const summaryText = `${prompt.title} - ${prompt.description || 'No description'}`
  const metaText = collectionName
    ? `Collection: ${collectionName} | Updated: ${new Date(prompt.updated_at).toLocaleString()}`
    : `Updated: ${new Date(prompt.updated_at).toLocaleString()}`

  return (
    <article className={styles.card}>
      <div className={styles.info}>
        <p className={styles.summary} title={summaryText}>
          {summaryText}
        </p>
        <p className={styles.meta}>{metaText}</p>
      </div>

      <div className={styles.actions}>
        <Button variant="secondary" onClick={() => onView(prompt)}>
          View
        </Button>
        <Button variant="secondary" onClick={() => onEdit(prompt)}>
          Edit
        </Button>
        <Button variant="danger" onClick={() => onDelete(prompt)}>
          Delete
        </Button>
      </div>
    </article>
  )
}

export default PromptCard
