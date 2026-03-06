import { useEffect, useState } from 'react'

import { getHealth } from '../api/health'
import AppHeader from '../components/layout/AppHeader'
import styles from './HomePage.module.css'

function HomePage() {
  const [health, setHealth] = useState(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function loadHealth() {
      try {
        const data = await getHealth()
        setHealth(data)
      } catch (requestError) {
        setError(requestError.message || 'Failed to connect to API')
      } finally {
        setIsLoading(false)
      }
    }

    loadHealth()
  }, [])

  return (
    <main className={styles.page}>
      <AppHeader />

      <section className={styles.card}>
        <h2>Frontend setup complete</h2>
        <p>
          This project now uses a modular folder structure, CSS Modules styling,
          and a reusable API client.
        </p>
      </section>

      <section className={styles.card}>
        <h3>Backend connection check</h3>
        {isLoading && <p>Checking API health...</p>}
        {!isLoading && error && <p className={styles.error}>{error}</p>}
        {!isLoading && health && (
          <p>
            API status: <strong>{health.status}</strong> (v{health.version})
          </p>
        )}
      </section>
    </main>
  )
}

export default HomePage
