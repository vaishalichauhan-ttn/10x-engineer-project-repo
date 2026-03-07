import Button from '../shared/Button'
import styles from './Header.module.css'

function Header({ onCreatePrompt, onOpenPrompts, onOpenCollections, currentPath, theme, onToggleTheme }) {
  const isDarkTheme = theme === 'dark'

  return (
    <header className={styles.header}>
      <div className={styles.topRow}>
        <div>
          <h1 className={styles.title}>Prompt Lab</h1>
          <p className={styles.subtitle}>Design, save, and organize prompt templates</p>
        </div>
        <div className={styles.themeSwitchWrap}>
          <span className={styles.themeLabel}>{isDarkTheme ? 'Dark' : 'Light'} mode</span>
          <label className={styles.themeSwitch}>
            <input
              type="checkbox"
              role="switch"
              checked={isDarkTheme}
              onChange={onToggleTheme}
              aria-label="Toggle theme mode"
            />
            <span className={styles.themeTrack} aria-hidden="true">
              <span className={styles.themeThumb} />
            </span>
          </label>
        </div>
      </div>

      <nav className={styles.menu} aria-label="Main menu">
        <Button
          variant={currentPath === '/' ? 'primary' : 'secondary'}
          onClick={onOpenPrompts}
          aria-pressed={currentPath === '/'}
        >
          Prompts
        </Button>
        <Button
          variant={currentPath === '/collections' ? 'primary' : 'secondary'}
          onClick={onOpenCollections}
          aria-pressed={currentPath === '/collections'}
        >
          Collections
        </Button>
        <Button onClick={onCreatePrompt}>New Prompt</Button>
      </nav>
    </header>
  )
}

export default Header
