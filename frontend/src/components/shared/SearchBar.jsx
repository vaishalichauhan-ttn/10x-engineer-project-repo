import styles from './SearchBar.module.css'

function SearchBar({ value, onChange, placeholder = 'Search prompts...' }) {
  return (
    <input
      type="search"
      className={styles.input}
      value={value}
      onChange={(event) => onChange(event.target.value)}
      placeholder={placeholder}
      aria-label={placeholder}
    />
  )
}

export default SearchBar
