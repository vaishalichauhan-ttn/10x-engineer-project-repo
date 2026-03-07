import Button from '../shared/Button'
import styles from './Header.module.css'

function Header({ onCreatePrompt, onOpenPrompts, onOpenCollections, currentPath }) {
  return (
    <header className={styles.header}>
      <div>
        <h1 className={styles.title}>PromptLab</h1>
        <p className={styles.subtitle}>Design, save, and organize prompt templates</p>
      </div>

      <nav className={styles.actions} aria-label="Primary navigation">
        <Button
          variant={currentPath === '/' ? 'primary' : 'secondary'}
          onClick={onOpenPrompts}
        >
          Prompts
        </Button>
        <Button
          variant={currentPath === '/collections' ? 'primary' : 'secondary'}
          onClick={onOpenCollections}
        >
          Collections
        </Button>
        <Button onClick={onCreatePrompt}>New Prompt</Button>
      </nav>
    </header>
  )
}

export default Header
