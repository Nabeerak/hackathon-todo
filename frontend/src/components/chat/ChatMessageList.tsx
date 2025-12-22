/**
 * Scrollable message list component for chat
 */

'use client';

import React, { useEffect, useRef } from 'react';
import type { ChatMessage as ChatMessageType } from '../../types/chat';
import { ChatMessage } from './ChatMessage';

interface ChatMessageListProps {
  messages: ChatMessageType[];
  loading?: boolean;
}

export function ChatMessageList({ messages, loading }: ChatMessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-2">
      {messages.length === 0 && !loading && (
        <div className="flex items-center justify-center h-full text-gray-400 text-sm">
          <div className="text-center">
            <p className="mb-2">👋 Hi! I'm your AI task assistant.</p>
            <p>Try saying "Add buy groceries tomorrow" or "What tasks are due today?"</p>
          </div>
        </div>
      )}

      {messages.map((message) => (
        <ChatMessage key={message.id} message={message} />
      ))}

      {loading && (
        <div className="flex justify-start">
          <div className="bg-gray-100 px-4 py-2 rounded-lg">
            <div className="flex gap-1">
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
              <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
