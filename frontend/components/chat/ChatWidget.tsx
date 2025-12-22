// T034: Create ChatWidget.tsx component with collapsible/expandable container, toggle button, fixed position bottom-right
// T042: Implement chat state management in ChatWidget using React useState
// T043: Handle AI proposed action response - display TaskActionConfirm dialog
// T045: Display error message in chat if OpenAI API unavailable (503 error)
// T061: Subscribe to task updates - refetch task list when AI action succeeds
// T062: Display AI confirmation message after successful update/complete/delete
// T070: Handle subtask creation from chat suggestions
// T072: Display proactive AI messages (overdue tasks) on session start
// T082: Subscribe to SSE events and display AI acknowledgment messages
// T084: Add keyboard shortcut (Cmd+K / Ctrl+K) to focus chat input
// T085: Persist chat widget open/closed state to localStorage (already implemented)
// T093: Add "AI Preferences" button to ChatWidget header that opens PreferencesDialog
// Phase 3 - User Story 1, 2, 3, 4 & 5: Natural Language Task Creation, Conversational Task Management, Task Context & Assistance, Multi-Modal Interaction & AI Learning & Personalization

"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import ChatInput from "./ChatInput";
import ChatMessageList from "./ChatMessageList";
import TaskActionConfirm from "./TaskActionConfirm";
import PreferencesDialog from "./PreferencesDialog"; // Phase 7 - AI Preferences
import { ChatClient, type UserPreferences, type QuotaResponse } from "@/lib/chatClient";
import { apiClient, TokenManager } from "@/lib/api";
import { getSSEClient } from "@/lib/websocket";
import type { ChatMessage, TaskAction } from "@/types/chat";
import type { SSEEvent } from "@/lib/websocket";
import type { Task } from "@/types/task";

interface ChatWidgetProps {
  onTaskCreated?: () => void;
  initialMessage?: string;
}

export default function ChatWidget({ onTaskCreated, initialMessage }: ChatWidgetProps) {
  // T034: Collapsible/expandable state
  const [isOpen, setIsOpen] = useState(false);

  // T042: Chat state management
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // T043: Pending action state
  const [pendingAction, setPendingAction] = useState<TaskAction | null>(null);
  const [isProcessingAction, setIsProcessingAction] = useState(false);

  // T072: Track if proactive messages have been shown
  const [proactiveMessagesShown, setProactiveMessagesShown] = useState(false);

  // T093: Preferences dialog state (Phase 7 - AI Preferences)
  const [isPreferencesOpen, setIsPreferencesOpen] = useState(false);
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [isSavingPreferences, setIsSavingPreferences] = useState(false);

  // T097: Quota state (Phase 8 - Polish)
  const [quota, setQuota] = useState<QuotaResponse | null>(null);

  // T084: Ref for chat input to enable keyboard shortcut
  const chatInputRef = useRef<HTMLInputElement>(null);

  const chatClient = new ChatClient();
  const sseClient = getSSEClient();

  // T071: Handle initialMessage - auto-open chat and send message
  useEffect(() => {
    if (initialMessage) {
      setIsOpen(true);
      // Small delay to ensure chat is visible before sending
      setTimeout(() => {
        handleSendMessage(initialMessage);
      }, 300);
    }
  }, [initialMessage]);

  // Load chat widget open/closed state from localStorage
  useEffect(() => {
    const savedState = localStorage.getItem("chatWidgetOpen");
    if (savedState !== null) {
      setIsOpen(savedState === "true");
    }
  }, []);

  // Save chat widget state to localStorage
  useEffect(() => {
    localStorage.setItem("chatWidgetOpen", String(isOpen));
  }, [isOpen]);

  // T072: Check for overdue tasks and display proactive message on session start
  useEffect(() => {
    if (proactiveMessagesShown) return;

    const checkOverdueTasks = async () => {
      try {
        const userId = TokenManager.getUserId();
        if (!userId) return;

        // Fetch all tasks
        const tasks = await apiClient.getTasks(userId);

        // Find overdue tasks (pending tasks with no explicit due date handling for now)
        // Since tasks don't have due_date in current schema, we'll check for old pending tasks
        const now = new Date();
        const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);

        const oldPendingTasks = tasks.filter((task: Task) => {
          if (task.is_completed) return false;
          const createdAt = new Date(task.created_at);
          return createdAt < oneDayAgo;
        });

        if (oldPendingTasks.length > 0) {
          // Display proactive message
          const proactiveMessage: ChatMessage = {
            id: `proactive-${Date.now()}`,
            user_id: "system",
            session_id: "current_session",
            content: `I noticed you have ${oldPendingTasks.length} pending task${oldPendingTasks.length > 1 ? 's' : ''} that ${oldPendingTasks.length > 1 ? 'were' : 'was'} created over a day ago. Would you like me to help you prioritize or break ${oldPendingTasks.length > 1 ? 'them' : 'it'} down?`,
            message_type: "system_notification",
            created_at: new Date().toISOString(),
            metadata: { proactive: true, task_count: oldPendingTasks.length },
          };

          setMessages((prev) => [...prev, proactiveMessage]);
          setProactiveMessagesShown(true);
        }
      } catch (err) {
        console.error("Failed to check for overdue tasks:", err);
        // Silent fail - proactive messages are optional
      }
    };

    // Small delay to avoid interfering with initial load
    const timer = setTimeout(checkOverdueTasks, 1000);
    return () => clearTimeout(timer);
  }, [proactiveMessagesShown]);

  // T082: SSE event handler to display AI acknowledgment messages
  const handleSSEEvent = useCallback((event: SSEEvent) => {
    console.log("SSE event received in ChatWidget:", event);

    // Generate acknowledgment message based on event type
    let acknowledgmentText = "";

    switch (event.event_type) {
      case "task_created":
        acknowledgmentText = `I see you created a new task: "${event.task?.title || 'Untitled'}"`;
        break;
      case "task_updated":
        acknowledgmentText = `I noticed you updated the task: "${event.task?.title || 'Untitled'}"`;
        break;
      case "task_completed":
        acknowledgmentText = `Great work! You completed: "${event.task?.title || 'Untitled'}"`;
        break;
      case "task_deleted":
        acknowledgmentText = `I see you deleted a task`;
        break;
      default:
        acknowledgmentText = `Task action detected`;
    }

    // Add acknowledgment message to chat
    const acknowledgmentMessage: ChatMessage = {
      id: `sse-ack-${Date.now()}`,
      user_id: "system",
      session_id: "current_session",
      content: acknowledgmentText,
      message_type: "ai_response",
      created_at: new Date().toISOString(),
      metadata: { sse_event: true, event_type: event.event_type },
    };

    setMessages((prev) => [...prev, acknowledgmentMessage]);

    // T083: Notify parent to refresh task list
    if (onTaskCreated) {
      onTaskCreated();
    }
  }, [onTaskCreated]);

  // T082: Connect to SSE on mount and subscribe to events
  useEffect(() => {
    // Register event handler
    sseClient.on("all", handleSSEEvent);

    // Connect to SSE (if not already connected)
    if (!sseClient.isConnected()) {
      sseClient.connect().catch((error) => {
        console.error("Failed to connect to SSE:", error);
        // Don't show error to user - SSE is optional enhancement
      });
    }

    // Cleanup: unregister handler on unmount
    return () => {
      sseClient.off("all", handleSSEEvent);
    };
  }, [handleSSEEvent, sseClient]);

  // Phase 7 - T093: Load user preferences on mount
  useEffect(() => {
    const loadPreferences = async () => {
      try {
        const prefs = await chatClient.getPreferences();
        setPreferences(prefs);
      } catch (err) {
        console.error("Failed to load preferences:", err);
        // Silent fail - preferences are optional
      }
    };
    loadPreferences();
  }, []);

  // Phase 8 - T097: Load quota information
  const loadQuota = useCallback(async () => {
    try {
      const quotaData = await chatClient.getQuota("day");
      setQuota(quotaData);
    } catch (err) {
      console.error("Failed to load quota:", err);
      // Silent fail - quota is informational only
    }
  }, [chatClient]);

  // Load quota on mount and when chat opens
  useEffect(() => {
    if (isOpen) {
      loadQuota();
    }
  }, [isOpen, loadQuota]);

  // T084: Keyboard shortcut (Cmd+K / Ctrl+K) to focus chat input
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Check for Cmd+K (Mac) or Ctrl+K (Windows/Linux)
      if ((event.metaKey || event.ctrlKey) && event.key === "k") {
        event.preventDefault();

        // Open chat if closed
        if (!isOpen) {
          setIsOpen(true);
        }

        // Focus input (with small delay if just opening)
        setTimeout(() => {
          chatInputRef.current?.focus();
        }, isOpen ? 0 : 100);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen]);

  const handleSendMessage = async (content: string) => {
    // T045: Clear any previous errors
    setError(null);

    // Add user message to UI immediately (optimistic update)
    const userMessage: ChatMessage = {
      id: `temp-${Date.now()}`,
      user_id: "current_user",
      session_id: "current_session",
      content,
      message_type: "user_message",
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // T039: Send message via ChatClient
      const response = await chatClient.sendMessage(content);

      // Update user message with actual ID from backend
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === userMessage.id
            ? { ...response.user_message, message_type: "user_message" }
            : msg
        )
      );

      // Add AI response message
      setMessages((prev) => [...prev, response.ai_response]);

      // T043: Handle proposed action
      if (response.proposed_action) {
        setPendingAction(response.proposed_action);
      }

      // T097: Refresh quota after sending message
      loadQuota();
    } catch (err) {
      // T045: Display error message in chat
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        user_id: "system",
        session_id: "current_session",
        content:
          err instanceof Error
            ? err.message
            : "Failed to send message. Please try again.",
        message_type: "system_notification",
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, errorMessage]);
      setError(
        err instanceof Error
          ? err.message
          : "Failed to send message. Please try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  // T062: Generate action-specific confirmation messages
  const getConfirmationMessage = (actionType: string, taskTitle?: string) => {
    const title = taskTitle || "the task";

    switch (actionType) {
      case "create":
        return `Done! I've created "${title}"`;
      case "update":
        return `Done! I've updated "${title}"`;
      case "complete":
        return `Done! I've marked "${title}" as complete`;
      case "delete":
        return `Done! I've deleted "${title}"`;
      case "query":
        return `Here are the tasks I found:`;
      default:
        return `Done! Action completed successfully.`;
    }
  };

  const handleConfirmAction = async () => {
    if (!pendingAction) return;

    setIsProcessingAction(true);
    setError(null);

    try {
      // T040: Confirm action via ChatClient
      const response = await chatClient.confirmAction(pendingAction.id);

      // T062: Add action-specific confirmation message
      const confirmMessage: ChatMessage = {
        id: `confirm-${Date.now()}`,
        user_id: "system",
        session_id: "current_session",
        content: getConfirmationMessage(
          pendingAction.action_type,
          response.task?.title || pendingAction.extracted_params?.title
        ),
        message_type: "ai_response",
        created_at: new Date().toISOString(),
        // Include query results in metadata if action was a query
        metadata: pendingAction.action_type === "query" && response.task
          ? { query_results: Array.isArray(response.task) ? response.task : [response.task] }
          : undefined,
      };

      setMessages((prev) => [...prev, confirmMessage]);
      setPendingAction(null);

      // T061: Notify parent to refresh task list for all action types
      if (onTaskCreated) {
        onTaskCreated();
      }
    } catch (err) {
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        user_id: "system",
        session_id: "current_session",
        content:
          err instanceof Error
            ? err.message
            : "Failed to confirm action. Please try again.",
        message_type: "system_notification",
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, errorMessage]);
      setError(
        err instanceof Error
          ? err.message
          : "Failed to confirm action. Please try again."
      );
    } finally {
      setIsProcessingAction(false);
    }
  };

  const handleRejectAction = async () => {
    if (!pendingAction) return;

    setIsProcessingAction(true);

    try {
      await chatClient.rejectAction(pendingAction.id);

      // Add rejection message
      const rejectMessage: ChatMessage = {
        id: `reject-${Date.now()}`,
        user_id: "system",
        session_id: "current_session",
        content: "Action rejected. How else can I help you?",
        message_type: "ai_response",
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, rejectMessage]);
      setPendingAction(null);
    } catch (err) {
      console.error("Failed to reject action:", err);
      // Silent fail - just close the dialog
      setPendingAction(null);
    } finally {
      setIsProcessingAction(false);
    }
  };

  // T070: Handle subtask creation from chat suggestions
  const handleCreateSubtask = async (title: string, description?: string) => {
    try {
      const userId = TokenManager.getUserId();
      if (!userId) {
        throw new Error("User not authenticated");
      }

      await apiClient.createTask(userId, { title, description });

      // Add confirmation message
      const confirmMessage: ChatMessage = {
        id: `subtask-created-${Date.now()}`,
        user_id: "system",
        session_id: "current_session",
        content: `Done! I've created the subtask "${title}"`,
        message_type: "ai_response",
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, confirmMessage]);

      // Notify parent to refresh task list
      if (onTaskCreated) {
        onTaskCreated();
      }
    } catch (err) {
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        user_id: "system",
        session_id: "current_session",
        content: `Failed to create subtask "${title}". Please try again.`,
        message_type: "system_notification",
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  // Phase 7 - T093: Handle saving preferences
  const handleSavePreferences = async (updatedPreferences: Partial<UserPreferences>) => {
    setIsSavingPreferences(true);
    try {
      const updated = await chatClient.updatePreferences(updatedPreferences);
      setPreferences(updated);
      setIsPreferencesOpen(false);
      // Add confirmation message to chat
      const confirmMessage: ChatMessage = {
        id: `prefs-saved-${Date.now()}`,
        user_id: "system",
        session_id: "current_session",
        content: "AI preferences updated successfully!",
        message_type: "system_notification",
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, confirmMessage]);
    } catch (err) {
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        user_id: "system",
        session_id: "current_session",
        content: "Failed to save preferences. Please try again.",
        message_type: "system_notification",
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsSavingPreferences(false);
    }
  };

  return (
    <>
      {/* T034: Fixed position bottom-right toggle button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 w-14 h-14 bg-[#8B0000] text-white rounded-full shadow-lg hover:bg-[#A01010] transition-all duration-200 flex items-center justify-center z-40"
          aria-label="Open chat"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
            />
          </svg>
        </button>
      )}

      {/* T034: Chat widget container */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-[#0A0A0A] border border-[#333333] rounded-lg shadow-2xl flex flex-col z-40">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-[#333333] bg-[#1A1A1A]">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <h3 className="font-semibold text-white">AI Assistant</h3>
            </div>
            <div className="flex items-center gap-2">
              {/* T093: AI Preferences button */}
              <button
                onClick={() => setIsPreferencesOpen(true)}
                className="text-[#CCCCCC] hover:text-white transition-colors"
                aria-label="AI Preferences"
                title="AI Preferences"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="text-[#CCCCCC] hover:text-white transition-colors"
                aria-label="Close chat"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
          </div>

          {/* T097: Quota warning banner */}
          {quota && quota.remaining <= 10 && (
            <div className="px-4 py-2 bg-yellow-900/20 border-b border-yellow-700/50">
              <div className="flex items-center gap-2 text-xs text-yellow-200">
                <svg
                  className="w-4 h-4 flex-shrink-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
                <span>
                  {quota.remaining === 0
                    ? "Daily AI request limit reached. Resets in " + new Date(quota.resets_at).toLocaleTimeString()
                    : `${quota.remaining} AI request${quota.remaining === 1 ? '' : 's'} remaining today`}
                </span>
              </div>
            </div>
          )}

          {/* Messages */}
          <ChatMessageList
            messages={messages}
            isLoading={isLoading}
            onCreateSubtask={handleCreateSubtask}
          />

          {/* Input */}
          <ChatInput
            ref={chatInputRef}
            onSend={handleSendMessage}
            disabled={isLoading}
            placeholder="Ask me to create a task..."
          />
        </div>
      )}

      {/* T043: Action confirmation dialog */}
      {pendingAction && (
        <TaskActionConfirm
          action={pendingAction}
          onConfirm={handleConfirmAction}
          onReject={handleRejectAction}
          isProcessing={isProcessingAction}
        />
      )}

      {/* T093: AI Preferences dialog */}
      <PreferencesDialog
        isOpen={isPreferencesOpen}
        onClose={() => setIsPreferencesOpen(false)}
        preferences={preferences}
        onSave={handleSavePreferences}
        isSaving={isSavingPreferences}
      />
    </>
  );
}
