import styles from './AppHeader.module.css'

function AppHeader() {
  return (
    <header className={styles.header}>
      <h1>PromptLab</h1>
      <p>Prompt engineering platform</p>
    </header>
  )
}

export default AppHeader
