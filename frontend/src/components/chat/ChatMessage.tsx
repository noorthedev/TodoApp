'use client';

import { memo } from 'react';
import { ChatMessage as ChatMessageType } from '../../lib/types';
import styles from './ChatMessage.module.css';

interface ChatMessageProps {
  message: ChatMessageType;
}

function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`${styles.messageContainer} ${isUser ? styles.user : styles.assistant}`}>
      <div className={styles.messageBubble}>
        <p className={styles.messageContent}>{message.content}</p>
        <span className={styles.timestamp}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    </div>
  );
}

export default memo(ChatMessage);
