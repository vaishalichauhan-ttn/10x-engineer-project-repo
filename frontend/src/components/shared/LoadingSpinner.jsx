import styles from './LoadingSpinner.module.css'

function LoadingSpinner({ label = 'Loading...' }) {
  return (
    <div className={styles.wrapper} role="status" aria-live="polite">
      <span className={styles.spinner} aria-hidden="true" />
      <span>{label}</span>
    </div>
  )
}

export default LoadingSpinner
