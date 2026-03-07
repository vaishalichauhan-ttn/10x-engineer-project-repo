import styles from './Sidebar.module.css'

function Sidebar({
  collections,
  selectedCollectionId,
  onSelectCollection,
  collectionActions,
}) {
  return (
    <aside className={styles.sidebar}>
      <div className={styles.header}>
        <h2>Collections</h2>
        {collectionActions}
      </div>

      <ul className={styles.list}>
        <li>
          <button
            className={selectedCollectionId ? styles.item : `${styles.item} ${styles.active}`}
            onClick={() => onSelectCollection(null)}
            type="button"
          >
            All Prompts
          </button>
        </li>
        {collections.map((collection) => (
          <li key={collection.id}>
            <button
              className={
                selectedCollectionId === collection.id
                  ? `${styles.item} ${styles.active}`
                  : styles.item
              }
              onClick={() => onSelectCollection(collection.id)}
              type="button"
            >
              {collection.name}
            </button>
          </li>
        ))}
      </ul>
    </aside>
  )
}

export default Sidebar
