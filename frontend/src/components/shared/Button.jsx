import styles from './Button.module.css'

function Button({
  children,
  type = 'button',
  variant = 'primary',
  onClick,
  disabled = false,
}) {
  const className = [styles.button, styles[variant], disabled ? styles.disabled : '']
    .filter(Boolean)
    .join(' ')

  return (
    <button type={type} className={className} onClick={onClick} disabled={disabled}>
      {children}
    </button>
  )
}

export default Button
