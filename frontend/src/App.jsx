import { useEffect, useMemo, useState } from 'react'

import CollectionForm from './components/collections/CollectionForm'
import CollectionList from './components/collections/CollectionList'
import Layout from './components/layout/Layout'
import PromptDetail from './components/prompts/PromptDetail'
import PromptForm from './components/prompts/PromptForm'
import PromptList from './components/prompts/PromptList'
import Button from './components/shared/Button'
import ErrorMessage from './components/shared/ErrorMessage'
import LoadingSpinner from './components/shared/LoadingSpinner'
import Modal from './components/shared/Modal'
import SearchBar from './components/shared/SearchBar'
import styles from './App.module.css'

const initialCollections = [
  { id: 'c1', name: 'Marketing' },
  { id: 'c2', name: 'Development' },
]

const initialPrompts = [
  {
    id: 'p1',
    title: 'Launch announcement',
    description: 'Draft a release announcement post for social media.',
    content: 'Write a LinkedIn launch announcement for PromptLab.',
    collection_id: 'c1',
    updated_at: new Date().toISOString(),
  },
  {
    id: 'p2',
    title: 'Code review helper',
    description: 'Summarize pull request changes and risk areas.',
    content: 'Review this PR diff and list potential regressions.',
    collection_id: 'c2',
    updated_at: new Date().toISOString(),
  },
]

function App() {
  const [currentPath, setCurrentPath] = useState(() =>
    window.location.pathname === '/collections' ? '/collections' : '/',
  )
  const [collections, setCollections] = useState(initialCollections)
  const [prompts, setPrompts] = useState(initialPrompts)
  const [selectedCollectionId, setSelectedCollectionId] = useState(null)
  const [selectedPrompt, setSelectedPrompt] = useState(null)
  const [promptPendingDelete, setPromptPendingDelete] = useState(null)
  const [collectionPendingDelete, setCollectionPendingDelete] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [modalMode, setModalMode] = useState('')
  const [editingPrompt, setEditingPrompt] = useState(null)
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    function handlePopState() {
      setCurrentPath(window.location.pathname === '/collections' ? '/collections' : '/')
      setModalMode('')
    }

    window.addEventListener('popstate', handlePopState)
    return () => window.removeEventListener('popstate', handlePopState)
  }, [])

  const visiblePrompts = useMemo(() => {
    return prompts.filter((prompt) => {
      const matchesCollection = selectedCollectionId
        ? prompt.collection_id === selectedCollectionId
        : true
      const normalizedSearch = searchQuery.trim().toLowerCase()
      const matchesSearch = normalizedSearch
        ? `${prompt.title} ${prompt.description || ''} ${prompt.content}`
            .toLowerCase()
            .includes(normalizedSearch)
        : true

      return matchesCollection && matchesSearch
    })
  }, [prompts, selectedCollectionId, searchQuery])

  const collectionNameById = useMemo(() => {
    return collections.reduce((map, collection) => {
      map[collection.id] = collection.name
      return map
    }, {})
  }, [collections])

  function navigate(path) {
    if (path === currentPath) {
      return
    }

    window.history.pushState({}, '', path)
    setCurrentPath(path)
    setModalMode('')
  }

  function closeModal() {
    setModalMode('')
    setEditingPrompt(null)
    setPromptPendingDelete(null)
    setCollectionPendingDelete(null)
  }

  function handleCreatePrompt() {
    if (currentPath !== '/') {
      navigate('/')
    }
    setEditingPrompt(null)
    setModalMode('promptForm')
  }

  function handleOpenPrompts() {
    navigate('/')
    setSelectedCollectionId(null)
  }

  function handleOpenCollections() {
    navigate('/collections')
  }

  function handleSavePrompt(formData) {
    if (editingPrompt) {
      const updatedPrompt = {
        ...editingPrompt,
        ...formData,
        updated_at: new Date().toISOString(),
      }
      setPrompts((current) =>
        current.map((prompt) => (prompt.id === editingPrompt.id ? updatedPrompt : prompt)),
      )
      if (selectedPrompt?.id === updatedPrompt.id) {
        setSelectedPrompt(updatedPrompt)
      }
    } else {
      const createdPrompt = {
        id: `p-${Date.now()}`,
        ...formData,
        updated_at: new Date().toISOString(),
      }
      setPrompts((current) => [createdPrompt, ...current])
    }

    closeModal()
  }

  function requestDeletePrompt(promptToDelete) {
    setPromptPendingDelete(promptToDelete)
    setModalMode('confirmDeletePrompt')
  }

  function confirmDeletePrompt() {
    if (!promptPendingDelete) {
      return
    }

    setPrompts((current) => current.filter((prompt) => prompt.id !== promptPendingDelete.id))
    if (selectedPrompt?.id === promptPendingDelete.id) {
      setSelectedPrompt(null)
    }
    closeModal()
  }

  function handleCreateCollection(formData) {
    const normalizedName = formData.name.trim().toLowerCase()
    const duplicate = collections.some(
      (collection) => collection.name.trim().toLowerCase() === normalizedName,
    )

    if (duplicate) {
      setErrorMessage('Collection names must be unique.')
      return
    }

    setCollections((current) => [...current, { id: `c-${Date.now()}`, ...formData }])
    setErrorMessage('')
  }

  function requestDeleteCollection(collection) {
    setCollectionPendingDelete(collection)
    setModalMode('confirmDeleteCollection')
  }

  function confirmDeleteCollection() {
    if (!collectionPendingDelete) {
      return
    }

    const collectionId = collectionPendingDelete.id

    setCollections((current) => current.filter((collection) => collection.id !== collectionId))
    setPrompts((current) =>
      current.map((prompt) =>
        prompt.collection_id === collectionId ? { ...prompt, collection_id: null } : prompt,
      ),
    )
    if (selectedCollectionId === collectionId) {
      setSelectedCollectionId(null)
    }
    closeModal()
  }

  const isPromptsRoute = currentPath === '/'

  return (
    <Layout
      onCreatePrompt={handleCreatePrompt}
      onOpenPrompts={handleOpenPrompts}
      onOpenCollections={handleOpenCollections}
      currentPath={currentPath}
    >
      <ErrorMessage message={errorMessage} />

      {isPromptsRoute ? (
        <>
          <div className={styles.toolbar}>
            <SearchBar value={searchQuery} onChange={setSearchQuery} placeholder="Search prompts" />
            <label className={styles.filter}>
              Collection
              <select
                value={selectedCollectionId || ''}
                onChange={(event) => setSelectedCollectionId(event.target.value || null)}
              >
                <option value="">All collections</option>
                {collections.map((collection) => (
                  <option key={collection.id} value={collection.id}>
                    {collection.name}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <PromptList
            prompts={visiblePrompts}
            collectionNameById={collectionNameById}
            onViewPrompt={(prompt) => {
              setSelectedPrompt(prompt)
              setModalMode('viewPrompt')
            }}
            onEditPrompt={(prompt) => {
              setEditingPrompt(prompt)
              setModalMode('promptForm')
            }}
            onDeletePrompt={requestDeletePrompt}
          />

          {prompts.length === 0 && <LoadingSpinner label="No prompts available yet" />}
        </>
      ) : (
        <section className={styles.collectionsPage}>
          <h2>Collections</h2>
          <CollectionForm onSubmit={handleCreateCollection} />
          <CollectionList
            collections={collections}
            onRequestDeleteCollection={requestDeleteCollection}
          />
        </section>
      )}

      <Modal
        isOpen={modalMode === 'promptForm'}
        title={editingPrompt ? 'Edit Prompt' : 'Create Prompt'}
        onClose={closeModal}
        showCloseButton={false}
      >
        <PromptForm
          initialData={editingPrompt}
          collections={collections}
          submitLabel={editingPrompt ? 'Update Prompt' : 'Create Prompt'}
          onSubmit={handleSavePrompt}
          onCancel={closeModal}
        />
      </Modal>

      <Modal isOpen={modalMode === 'viewPrompt'} title="Prompt Details" onClose={closeModal}>
        <PromptDetail prompt={selectedPrompt} />
      </Modal>

      <Modal
        isOpen={modalMode === 'confirmDeletePrompt'}
        title="Delete Prompt"
        onClose={closeModal}
        footer={
          <>
            <Button variant="secondary" onClick={closeModal}>
              Cancel
            </Button>
            <Button variant="danger" onClick={confirmDeletePrompt}>
              Delete
            </Button>
          </>
        }
      >
        <p className={styles.confirmationText}>
          Are you sure you want to delete{' '}
          <strong>{promptPendingDelete?.title || 'this prompt'}</strong>?
        </p>
      </Modal>

      <Modal
        isOpen={modalMode === 'confirmDeleteCollection'}
        title="Delete Collection"
        onClose={closeModal}
        footer={
          <>
            <Button variant="secondary" onClick={closeModal}>
              Cancel
            </Button>
            <Button variant="danger" onClick={confirmDeleteCollection}>
              Delete
            </Button>
          </>
        }
      >
        <p className={styles.confirmationText}>
          Are you sure you want to delete{' '}
          <strong>{collectionPendingDelete?.name || 'this collection'}</strong>?
        </p>
      </Modal>
    </Layout>
  )
}

export default App
