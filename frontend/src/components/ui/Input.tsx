interface InputProps {
  id?: string;
  type?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  minLength?: number;
  maxLength?: number;
  style?: React.CSSProperties;
}

export default function Input({
  id,
  type = 'text',
  value,
  onChange,
  placeholder,
  required = false,
  disabled = false,
  minLength,
  maxLength,
  style = {}
}: InputProps) {
  const baseStyle: React.CSSProperties = {
    width: '100%',
    padding: '0.5rem',
    border: '1px solid #ccc',
    borderRadius: '4px',
    fontSize: '1rem',
    transition: 'border-color 0.2s',
    ...style
  };

  return (
    <input
      id={id}
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      required={required}
      disabled={disabled}
      minLength={minLength}
      maxLength={maxLength}
      style={baseStyle}
      onFocus={(e) => e.target.style.borderColor = '#0070f3'}
      onBlur={(e) => e.target.style.borderColor = '#ccc'}
    />
  );
}
