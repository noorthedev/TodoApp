'use client';

import { useState, useCallback } from 'react';
import apiClient from '../lib/api';
import { ChatMessage, ChatRequest, ChatResponse } from '../lib/types';

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [inputValue, setInputValue] = useState('');

  const sendMessage = useCallback(async (message: string) => {
    if (!message.trim()) return;

    setError(null);
    setLoading(true);

    // Add user message immediately
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: message,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      const requestData: ChatRequest = {
        message,
        ...(conversationId && { conversation_id: conversationId }),
      };

      const response = await apiClient.post<ChatResponse>('/api/chat', requestData);

      // Add assistant message
      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);

      // Store conversation ID
      if (!conversationId) {
        setConversationId(response.data.conversation_id);
      }

      return response.data.response;
    } catch (err: any) {
      let errorMessage = 'Failed to send message. Please try again.';

      if (err.response?.status === 401) {
        errorMessage = 'Your session has expired. Please log in again.';
      } else if (err.response?.status >= 500) {
        errorMessage = 'Server error. Please try again.';
      } else if (err.code === 'ECONNABORTED') {
        errorMessage = 'Request timed out. Please try again.';
      }

      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [conversationId]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    messages,
    conversationId,
    loading,
    error,
    inputValue,
    setInputValue,
    sendMessage,
    clearError,
  };
}
