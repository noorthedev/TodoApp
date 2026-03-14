'use client';

import { useCallback } from 'react';
import { useChat } from '../../hooks/useChat';
import ChatHistory from './ChatHistory';
import ChatInput from './ChatInput';
import styles from './ChatPanel.module.css';

interface ChatPanelProps {
  onTaskOperation?: () => void;
}

const TASK_KEYWORDS = ['created', 'added', 'updated', 'modified', 'deleted', 'removed', 'marked complete', 'completed'];

export default function ChatPanel({ onTaskOperation }: ChatPanelProps) {
  const {
    messages,
    loading,
    error,
    inputValue,
    setInputValue,
    sendMessage,
    clearError,
  } = useChat();

  const handleSubmit = useCallback(async () => {
    const message = inputValue.trim();
    if (!message || loading) return;

    setInputValue('');

    try {
      const response = await sendMessage(message);

      // Check if response indicates task operation
      if (response && onTaskOperation) {
        const lowerResponse = response.toLowerCase();
        const hasTaskOperation = TASK_KEYWORDS.some(keyword =>
          lowerResponse.includes(keyword)
        );

        if (hasTaskOperation) {
          // Debounce refresh
          setTimeout(() => {
            onTaskOperation();
          }, 500);
        }
      }
    } catch (err) {
      // Error already handled in useChat
    }
  }, [inputValue, loading, sendMessage, setInputValue, onTaskOperation]);

  return (
    <div className={styles.chatPanel}>
      <div className={styles.header}>
        <h2>AI Assistant</h2>
      </div>

      <ChatHistory messages={messages} loading={loading} />

      {error && (
        <div className={styles.errorContainer}>
          <p>{error}</p>
          <button onClick={clearError}>Dismiss</button>
        </div>
      )}

      <ChatInput
        value={inputValue}
        onChange={setInputValue}
        onSubmit={handleSubmit}
        disabled={loading}
        placeholder="Ask me to manage your tasks..."
      />
    </div>
  );
}
