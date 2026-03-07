import PromptCard from './PromptCard'
import styles from './PromptList.module.css'

function PromptList({
  prompts,
  collectionNameById,
  onViewPrompt,
  onEditPrompt,
  onDeletePrompt,
}) {
  if (prompts.length === 0) {
    return <p className={styles.empty}>No prompts found for this view.</p>
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
