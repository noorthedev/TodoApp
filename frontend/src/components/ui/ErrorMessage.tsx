interface ErrorMessageProps {
  message: string;
  onDismiss?: () => void;
}

export default function ErrorMessage({ message, onDismiss }: ErrorMessageProps) {
  return (
    <div style={{
      padding: '1rem',
      backgroundColor: '#fee',
      color: '#c00',
      border: '1px solid #fcc',
      borderRadius: '4px',
      marginBottom: '1rem',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center'
    }}>
      <span>{message}</span>
      {onDismiss && (
        <button
          onClick={onDismiss}
          style={{
            background: 'none',
            border: 'none',
            color: '#c00',
            cursor: 'pointer',
            fontSize: '1.2rem',
            padding: '0 0.5rem'
          }}
          aria-label="Dismiss error"
        >
          ×
        </button>
      )}
    </div>
  );
}
