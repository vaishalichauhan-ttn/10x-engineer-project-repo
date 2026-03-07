import { useEffect, useMemo, useState } from 'react'

import { createCollection, deleteCollection, getCollections } from './api/collections'
import { createPrompt, deletePrompt, getPrompt, getPrompts, updatePrompt } from './api/prompts'
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

function normalizePromptPayload(formData) {
  return {
    title: formData.title.trim(),
    content: formData.content.trim(),
    description: formData.description?.trim() || null,
    collection_id: formData.collection_id || null,
  }
}

function App() {
  const [currentPath, setCurrentPath] = useState(() =>
    window.location.pathname === '/collections' ? '/collections' : '/',
  )
  const [collections, setCollections] = useState([])
  const [prompts, setPrompts] = useState([])
  const [isLoadingData, setIsLoadingData] = useState(true)
  const [selectedCollectionId, setSelectedCollectionId] = useState(null)
  const [selectedPrompt, setSelectedPrompt] = useState(null)
  const [promptPendingDelete, setPromptPendingDelete] = useState(null)
  const [collectionPendingDelete, setCollectionPendingDelete] = useState(null)
  const [isLoadingPromptDetail, setIsLoadingPromptDetail] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [modalMode, setModalMode] = useState('')
  const [editingPrompt, setEditingPrompt] = useState(null)
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    async function loadInitialData() {
      try {
        setErrorMessage('')
        const [collectionsData, promptsData] = await Promise.all([
          getCollections(),
          getPrompts(),
        ])
        setCollections(collectionsData)
        setPrompts(promptsData)
      } catch (error) {
        setErrorMessage(error.message || 'Failed to load application data.')
      } finally {
        setIsLoadingData(false)
      }
    }

    loadInitialData()
  }, [])

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
    setIsLoadingPromptDetail(false)
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

  async function handleSavePrompt(formData) {
    const payload = normalizePromptPayload(formData)

    try {
      setErrorMessage('')

      if (editingPrompt) {
        const updatedPrompt = await updatePrompt(editingPrompt.id, payload)
        setPrompts((current) =>
          current.map((prompt) => (prompt.id === editingPrompt.id ? updatedPrompt : prompt)),
        )
        if (selectedPrompt?.id === updatedPrompt.id) {
          setSelectedPrompt(updatedPrompt)
        }
      } else {
        const createdPrompt = await createPrompt(payload)
        setPrompts((current) => [createdPrompt, ...current])
      }

      closeModal()
    } catch (error) {
      setErrorMessage(error.message || 'Failed to save prompt.')
    }
  }

  function requestDeletePrompt(promptToDelete) {
    setPromptPendingDelete(promptToDelete)
    setModalMode('confirmDeletePrompt')
  }

  async function handleViewPrompt(prompt) {
    setSelectedPrompt(prompt)
    setModalMode('viewPrompt')
    setIsLoadingPromptDetail(true)

    try {
      setErrorMessage('')
      const latestPrompt = await getPrompt(prompt.id)
      setSelectedPrompt(latestPrompt)
    } catch (error) {
      setErrorMessage(error.message || 'Failed to load prompt details.')
    } finally {
      setIsLoadingPromptDetail(false)
    }
  }

  async function confirmDeletePrompt() {
    if (!promptPendingDelete) {
      return
    }

    try {
      setErrorMessage('')
      await deletePrompt(promptPendingDelete.id)
      setPrompts((current) => current.filter((prompt) => prompt.id !== promptPendingDelete.id))
      if (selectedPrompt?.id === promptPendingDelete.id) {
        setSelectedPrompt(null)
      }
      closeModal()
    } catch (error) {
      setErrorMessage(error.message || 'Failed to delete prompt.')
    }
  }

  async function handleCreateCollection(formData) {
    const normalizedName = formData.name.trim().toLowerCase()
    const duplicate = collections.some(
      (collection) => collection.name.trim().toLowerCase() === normalizedName,
    )

    if (duplicate) {
      setErrorMessage('Collection names must be unique.')
      return
    }

    try {
      setErrorMessage('')
      const createdCollection = await createCollection({
        name: formData.name.trim(),
      })
      setCollections((current) => [...current, createdCollection])
    } catch (error) {
      setErrorMessage(error.message || 'Failed to create collection.')
    }
  }

  function requestDeleteCollection(collection) {
    setCollectionPendingDelete(collection)
    setModalMode('confirmDeleteCollection')
  }

  async function confirmDeleteCollection() {
    if (!collectionPendingDelete) {
      return
    }

    try {
      setErrorMessage('')
      const collectionId = collectionPendingDelete.id
      await deleteCollection(collectionId)

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
    } catch (error) {
      setErrorMessage(error.message || 'Failed to delete collection.')
    }
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

      {isLoadingData ? (
        <LoadingSpinner label="Loading data..." />
      ) : isPromptsRoute ? (
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
            onViewPrompt={handleViewPrompt}
            onEditPrompt={(prompt) => {
              setEditingPrompt(prompt)
              setModalMode('promptForm')
            }}
            onDeletePrompt={requestDeletePrompt}
          />
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
        {isLoadingPromptDetail ? (
          <LoadingSpinner label="Loading prompt details..." />
        ) : (
          <PromptDetail prompt={selectedPrompt} />
        )}
      </Modal>

      <Modal
        isOpen={modalMode === 'confirmDeletePrompt'}
        title="Delete Prompt"
        onClose={closeModal}
        showCloseButton={false}
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
        showCloseButton={false}
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
