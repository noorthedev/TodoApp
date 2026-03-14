'use client';

import { useEffect, useRef } from 'react';
import { ChatMessage as ChatMessageType } from '../../lib/types';
import ChatMessage from './ChatMessage';
import styles from './ChatPanel.module.css';

interface ChatHistoryProps {
  messages: ChatMessageType[];
  loading: boolean;
}

export default function ChatHistory({ messages, loading }: ChatHistoryProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) return;

    const isNearBottom =
      container.scrollHeight - container.scrollTop - container.clientHeight < 100;

    if (isNearBottom) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  return (
    <div className={styles.messagesContainer} ref={messagesContainerRef}>
      {messages.length === 0 && (
        <div className={styles.emptyState}>
          <p>👋 Hi! I can help you manage your tasks.</p>
          <p>Try saying: "Add a task to buy groceries"</p>
        </div>
      )}

      {messages.map((message) => (
        <ChatMessage key={message.id} message={message} />
      ))}

      {loading && (
        <div className={styles.loadingIndicator}>
          <span>AI is thinking...</span>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}
