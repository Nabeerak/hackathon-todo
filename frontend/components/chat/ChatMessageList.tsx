// T037: Create ChatMessageList.tsx component for scrollable message history
// T070: Pass onCreateSubtask to ChatMessage components
// Phase 3 - User Story 1 & 3: Natural Language Task Creation & Task Context & Assistance

"use client";

import { useEffect, useRef } from "react";
import ChatMessage from "./ChatMessage";
import type { ChatMessage as ChatMessageType } from "@/types/chat";

interface ChatMessageListProps {
  messages: ChatMessageType[];
  isLoading?: boolean;
  onCreateSubtask?: (title: string, description?: string) => Promise<void>;
}

export default function ChatMessageList({
  messages,
  isLoading = false,
  onCreateSubtask,
}: ChatMessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="text-center space-y-3">
          <div className="flex justify-center">
            <svg
              className="w-12 h-12 text-[#8B0000]"
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
          </div>
          <p className="text-sm text-[#CCCCCC]">
            Start a conversation with the AI assistant
          </p>
          <p className="text-xs text-[#999999]">
            Try: &quot;Add buy groceries tomorrow&quot;
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-2 scroll-smooth">
      {messages.map((message) => (
        <ChatMessage key={message.id} message={message} onCreateSubtask={onCreateSubtask} />
      ))}

      {/* Loading indicator */}
      {isLoading && (
        <div className="flex justify-start mb-4">
          <div className="bg-[#1A1A1A] border border-[#333333] rounded-lg px-4 py-3">
            <div className="flex items-center space-x-2">
              <div className="flex space-x-1">
                <div
                  className="w-2 h-2 bg-[#8B0000] rounded-full animate-bounce"
                  style={{ animationDelay: "0ms" }}
                />
                <div
                  className="w-2 h-2 bg-[#8B0000] rounded-full animate-bounce"
                  style={{ animationDelay: "150ms" }}
                />
                <div
                  className="w-2 h-2 bg-[#8B0000] rounded-full animate-bounce"
                  style={{ animationDelay: "300ms" }}
                />
              </div>
              <span className="text-xs text-[#CCCCCC]">AI is thinking...</span>
            </div>
          </div>
        </div>
      )}

      {/* Scroll anchor */}
      <div ref={messagesEndRef} />
    </div>
  );
}
