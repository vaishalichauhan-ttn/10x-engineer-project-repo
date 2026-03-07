import styles from './Button.module.css'

function Button({
  children,
  type = 'button',
  variant = 'primary',
  onClick,
  disabled = false,
  ...rest
}) {
  const className = [styles.button, styles[variant], disabled ? styles.disabled : '']
    .filter(Boolean)
    .join(' ')

  return (
    <button
      type={type}
      className={className}
      onClick={onClick}
      disabled={disabled}
      {...rest}
    >
      {children}
    </button>
  )
}

export default Button
