import { useEffect, useId, useRef } from 'react'

import Button from './Button'
import styles from './Modal.module.css'

function Modal({ isOpen, title, children, onClose, footer, showCloseButton = true }) {
  const dialogRef = useRef(null)
  const previouslyFocusedRef = useRef(null)
  const titleId = useId()

  function getFocusableElements() {
    if (!dialogRef.current) {
      return []
    }

    return Array.from(
      dialogRef.current.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
      ),
    ).filter((element) => !element.hasAttribute('disabled'))
  }

  useEffect(() => {
    if (!isOpen) {
      return undefined
    }

    previouslyFocusedRef.current = document.activeElement
    const focusableElements = getFocusableElements()
    if (focusableElements.length > 0) {
      focusableElements[0].focus()
    } else if (dialogRef.current) {
      dialogRef.current.focus()
    }

    function handleEscape(event) {
      if (event.key === 'Escape') {
        onClose()
      }

      if (event.key === 'Tab') {
        const elements = getFocusableElements()
        if (elements.length === 0) {
          event.preventDefault()
          return
        }

        const firstElement = elements[0]
        const lastElement = elements[elements.length - 1]

        if (event.shiftKey && document.activeElement === firstElement) {
          event.preventDefault()
          lastElement.focus()
        } else if (!event.shiftKey && document.activeElement === lastElement) {
          event.preventDefault()
          firstElement.focus()
        }
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => {
      document.removeEventListener('keydown', handleEscape)
      if (previouslyFocusedRef.current && previouslyFocusedRef.current.focus) {
        previouslyFocusedRef.current.focus()
      }
    }
  }, [isOpen, onClose])

  if (!isOpen) {
    return null
  }

  return (
    <div className={styles.backdrop} onClick={onClose} role="presentation">
      <div
        ref={dialogRef}
        className={styles.dialog}
        onClick={(event) => event.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        tabIndex={-1}
      >
        <div className={styles.header}>
          <h3 id={titleId}>{title}</h3>
          {showCloseButton && (
            <Button variant="secondary" onClick={onClose}>
              Close
            </Button>
          )}
        </div>

        <div className={styles.body}>{children}</div>

        {footer && <div className={styles.footer}>{footer}</div>}
      </div>
    </div>
  )
}

export default Modal
