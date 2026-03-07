import PromptCard from './PromptCard'
import styles from './PromptList.module.css'

function PromptList({
  prompts,
  hasAnyPrompts,
  hasFilters,
  collectionNameById,
  onViewPrompt,
  onEditPrompt,
  onDeletePrompt,
  onCreatePrompt,
}) {
  if (prompts.length === 0) {
    if (!hasAnyPrompts) {
      return (
        <div className={styles.emptyState}>
          <p className={styles.emptyTitle}>No prompts yet</p>
          <p className={styles.emptyText}>Create your first prompt to get started.</p>
          <button className={styles.emptyAction} type="button" onClick={onCreatePrompt}>
            Create Prompt
          </button>
        </div>
      )
    }

    return (
      <p className={styles.empty} role="status" aria-live="polite">
        {hasFilters ? 'No prompts match your current filters.' : 'No prompts found.'}
      </p>
    )
  }

  return (
    <div className={styles.list}>
      {prompts.map((prompt) => (
        <PromptCard
          key={prompt.id}
          prompt={prompt}
          collectionName={collectionNameById[prompt.collection_id]}
          onView={onViewPrompt}
          onEdit={onEditPrompt}
          onDelete={onDeletePrompt}
        />
      ))}
    </div>
  )
}

export default PromptList
