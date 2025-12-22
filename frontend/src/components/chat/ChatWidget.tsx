/**
 * Main Chat Widget component with error boundary and quota warning
 * Implements T097, T099, T100
 */

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { chatClient } from '../../lib/chatClient';
import type { ChatMessage, TaskAction, QuotaInfo } from '../../types/chat';
import { ChatErrorBoundary } from './ChatErrorBoundary';
import { QuotaWarning } from './QuotaWarning';
import { ChatMessageList } from './ChatMessageList';
import { ChatInput } from './ChatInput';
import { TaskActionConfirm } from './TaskActionConfirm';

interface ChatWidgetProps {
  onTaskUpdated?: () => void;
}

function ChatWidgetInner({ onTaskUpdated }: ChatWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pendingAction, setPendingAction] = useState<TaskAction | null>(null);
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [quota, setQuota] = useState<QuotaInfo | null>(null);
  const [quotaLoading, setQuotaLoading] = useState(false);
  const [aiAvailable, setAiAvailable] = useState(true);

  // Load quota on mount and when chat opens
  const loadQuota = useCallback(async () => {
    setQuotaLoading(true);
    try {
      const quotaData = await chatClient.getQuota();
      setQuota(quotaData);
    } catch (err) {
      console.error('Failed to load quota:', err);
      // Don't show error for quota - it's not critical
    } finally {
      setQuotaLoading(false);
    }
  }, []);

  // Check AI health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await chatClient.getHealth();
        setAiAvailable(health.openai_available);
      } catch (err) {
        console.error('Failed to check AI health:', err);
        setAiAvailable(false);
      }
    };

    checkHealth();
  }, []);

  // Load quota when widget opens
  useEffect(() => {
    if (isOpen && !quota) {
      loadQuota();
    }
  }, [isOpen, quota, loadQuota]);

  // Persist open/closed state to localStorage
  useEffect(() => {
    const saved = localStorage.getItem('chat_widget_open');
    if (saved !== null) {
      setIsOpen(saved === 'true');
    }
  }, []);

  const toggleOpen = () => {
    const newState = !isOpen;
    setIsOpen(newState);
    localStorage.setItem('chat_widget_open', String(newState));
  };

  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await chatClient.sendMessage({
        content,
        session_id: sessionId || undefined,
      });

      // Update session ID
      if (!sessionId) {
        setSessionId(response.session_id);
      }

      // Add messages to list
      setMessages((prev) => [...prev, response.user_message, response.ai_response]);

      // Handle proposed action
      if (response.proposed_action) {
        setPendingAction(response.proposed_action);
      }

      // Refresh quota after each message
      loadQuota();
    } catch (err: any) {
      console.error('Failed to send message:', err);

      // Check if it's a service unavailable error
      if (err.message.includes('503') || err.message.includes('configured')) {
        setError('AI service is currently unavailable. Please use the traditional form to manage tasks.');
        setAiAvailable(false);
      } else {
        setError(err.message || 'Failed to send message. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmAction = async () => {
    if (!pendingAction) return;

    setConfirmLoading(true);
    setError(null);

    try {
      const response = await chatClient.confirmAction(pendingAction.action_id);

      // Add confirmation message
      const confirmMessage: ChatMessage = {
        id: `confirm-${Date.now()}`,
        user_id: 0,
        session_id: sessionId || '',
        content: response.error
          ? `Failed to execute action: ${response.error}`
          : `✓ ${getConfirmationMessage(pendingAction.action_type)}`,
        message_type: 'system_notification',
        created_at: new Date().toISOString(),
        metadata: {},
      };

      setMessages((prev) => [...prev, confirmMessage]);
      setPendingAction(null);

      // Refresh task list if callback provided
      if (onTaskUpdated && !response.error) {
        onTaskUpdated();
      }

      // Refresh quota
      loadQuota();
    } catch (err: any) {
      console.error('Failed to confirm action:', err);
      setError(err.message || 'Failed to execute action. Please try again.');
    } finally {
      setConfirmLoading(false);
    }
  };

  const handleRejectAction = async () => {
    if (!pendingAction) return;

    setConfirmLoading(true);
    setError(null);

    try {
      await chatClient.rejectAction(pendingAction.action_id);

      // Add rejection message
      const rejectMessage: ChatMessage = {
        id: `reject-${Date.now()}`,
        user_id: 0,
        session_id: sessionId || '',
        content: 'Action cancelled.',
        message_type: 'system_notification',
        created_at: new Date().toISOString(),
        metadata: {},
      };

      setMessages((prev) => [...prev, rejectMessage]);
      setPendingAction(null);
    } catch (err: any) {
      console.error('Failed to reject action:', err);
      setError(err.message || 'Failed to cancel action.');
    } finally {
      setConfirmLoading(false);
    }
  };

  const getConfirmationMessage = (actionType: string): string => {
    switch (actionType) {
      case 'create':
        return 'Task created successfully!';
      case 'update':
        return 'Task updated successfully!';
      case 'complete':
        return 'Task marked as complete!';
      case 'delete':
        return 'Task deleted successfully!';
      case 'query':
        return 'Query executed!';
      default:
        return 'Action completed!';
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={toggleOpen}
        className="fixed bottom-6 right-6 w-14 h-14 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-all flex items-center justify-center z-50"
        aria-label="Open AI Chat"
      >
        <svg
          className="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
          />
        </svg>
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-white rounded-lg shadow-2xl flex flex-col z-50 border border-gray-200">
      {/* Header */}
      <div className="bg-blue-600 text-white p-4 rounded-t-lg flex items-center justify-between">
        <div>
          <h3 className="font-semibold">AI Task Assistant</h3>
          {!aiAvailable && (
            <p className="text-xs text-blue-100">Service unavailable</p>
          )}
        </div>
        <button
          onClick={toggleOpen}
          className="text-white hover:bg-blue-700 rounded p-1"
          aria-label="Close chat"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Quota Warning - T097 */}
      {isOpen && (
        <div className="px-4 pt-4">
          <QuotaWarning quota={quota} loading={quotaLoading} />
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mx-4 mt-2 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* AI Unavailable Warning - T100 */}
      {!aiAvailable && (
        <div className="mx-4 mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded text-yellow-800 text-sm">
          AI service is unavailable. Please use the traditional form to manage your tasks.
        </div>
      )}

      {/* Messages */}
      <ChatMessageList messages={messages} loading={loading} />

      {/* Pending Action Confirmation */}
      {pendingAction && (
        <TaskActionConfirm
          action={pendingAction}
          onConfirm={handleConfirmAction}
          onReject={handleRejectAction}
          loading={confirmLoading}
        />
      )}

      {/* Input */}
      <ChatInput
        onSend={handleSendMessage}
        disabled={loading || confirmLoading || !aiAvailable}
        placeholder={aiAvailable ? 'Type a message...' : 'AI service unavailable'}
      />
    </div>
  );
}

// Export with error boundary - T099
export function ChatWidget(props: ChatWidgetProps) {
  return (
    <ChatErrorBoundary>
      <ChatWidgetInner {...props} />
    </ChatErrorBoundary>
  );
}
