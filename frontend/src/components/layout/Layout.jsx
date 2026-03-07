import Header from './Header'
import styles from './Layout.module.css'

function Layout({
  children,
  onCreatePrompt,
  onOpenPrompts,
  onOpenCollections,
  currentPath,
  theme,
  onToggleTheme,
}) {
  return (
    <div className={styles.page}>
      <Header
        onCreatePrompt={onCreatePrompt}
        onOpenPrompts={onOpenPrompts}
        onOpenCollections={onOpenCollections}
        currentPath={currentPath}
        theme={theme}
        onToggleTheme={onToggleTheme}
      />

      <section className={styles.main}>{children}</section>
    </div>
  )
}

export default Layout
