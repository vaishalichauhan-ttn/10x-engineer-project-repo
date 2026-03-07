import styles from './PromptDetail.module.css'

function PromptDetail({ prompt }) {
  if (!prompt) {
    return <p className={styles.empty}>Select a prompt to view details.</p>
  }

  return (
    <section className={styles.detail}>
      <h2>{prompt.title}</h2>
      {prompt.description && <p className={styles.description}>{prompt.description}</p>}
      <pre>{prompt.content}</pre>
    </section>
  )
}

export default PromptDetail
