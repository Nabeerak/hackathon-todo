// T036: Create ChatMessage.tsx component to display message bubbles (user vs AI styling)
// T057: Update ChatMessage.tsx to display query results (task list) formatted as bullet points or table
// T070: Update ChatMessage.tsx to render subtask suggestions as interactive checkboxes
// T073: Add pattern insights display in chat
// Phase 3 - User Story 1 & 3: Natural Language Task Creation & Task Context & Assistance

"use client";

import { useState } from "react";
import type { ChatMessage as ChatMessageType } from "@/types/chat";
import type { Task } from "@/types/task";

interface SubtaskSuggestion {
  title: string;
  description?: string;
}

interface PatternInsight {
  pattern_type: string;
  description: string;
  frequency?: number;
  examples?: string[];
}

interface ChatMessageProps {
  message: ChatMessageType;
  onCreateSubtask?: (title: string, description?: string) => Promise<void>;
}

export default function ChatMessage({ message, onCreateSubtask }: ChatMessageProps) {
  const isUser = message.message_type === "user_message";
  const isSystem = message.message_type === "system_notification";

  // T057: Check if message contains query results in metadata
  const queryResults = message.metadata?.query_results as Task[] | undefined;
  const hasQueryResults = queryResults && queryResults.length > 0;

  // T070: Check if message contains subtask suggestions in metadata
  const subtaskSuggestions = message.metadata?.subtask_suggestions as SubtaskSuggestion[] | undefined;
  const hasSubtaskSuggestions = subtaskSuggestions && subtaskSuggestions.length > 0;

  // T073: Check if message contains pattern insights in metadata
  const patternInsights = message.metadata?.pattern_insights as PatternInsight[] | undefined;
  const hasPatternInsights = patternInsights && patternInsights.length > 0;

  // T070: Track loading state for subtask creation
  const [creatingSubtasks, setCreatingSubtasks] = useState<Set<number>>(new Set());

  // T070: Handle subtask checkbox click
  const handleCreateSubtask = async (index: number, suggestion: SubtaskSuggestion) => {
    if (!onCreateSubtask || creatingSubtasks.has(index)) return;

    setCreatingSubtasks((prev) => new Set(prev).add(index));
    try {
      await onCreateSubtask(suggestion.title, suggestion.description);
    } finally {
      setCreatingSubtasks((prev) => {
        const next = new Set(prev);
        next.delete(index);
        return next;
      });
    }
  };

  const renderQueryResults = () => {
    if (!queryResults || queryResults.length === 0) {
      return null;
    }

    return (
      <div className="mt-3 space-y-2">
        <div className="text-xs text-[#999999] font-semibold mb-2">
          Found {queryResults.length} task{queryResults.length !== 1 ? "s" : ""}:
        </div>
        <div className="space-y-2">
          {queryResults.map((task) => (
            <div
              key={task.id}
              className="bg-[#2A2A2A] border border-[#444444] rounded-lg p-3 text-sm"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        task.is_completed ? "bg-green-500" : "bg-yellow-500"
                      }`}
                    />
                    <span className="font-medium text-white">{task.title}</span>
                  </div>
                  {task.description && (
                    <p className="text-xs text-[#CCCCCC] mt-1 ml-4">
                      {task.description}
                    </p>
                  )}
                </div>
                <span
                  className={`text-xs px-2 py-0.5 rounded ${
                    task.is_completed
                      ? "bg-green-900/30 text-green-400"
                      : "bg-yellow-900/30 text-yellow-400"
                  }`}
                >
                  {task.is_completed ? "Done" : "Pending"}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  // T070: Render subtask suggestions as interactive checkboxes
  const renderSubtaskSuggestions = () => {
    if (!subtaskSuggestions || subtaskSuggestions.length === 0) {
      return null;
    }

    return (
      <div className="mt-3 space-y-2">
        <div className="text-xs text-[#999999] font-semibold mb-2">
          Suggested subtasks (click to create):
        </div>
        <div className="space-y-2">
          {subtaskSuggestions.map((suggestion, index) => {
            const isCreating = creatingSubtasks.has(index);
            return (
              <button
                key={index}
                onClick={() => handleCreateSubtask(index, suggestion)}
                disabled={isCreating || !onCreateSubtask}
                className="w-full bg-[#2A2A2A] border border-[#444444] rounded-lg p-3 text-sm hover:border-[#8B0000] hover:bg-[#8B0000]/10 transition-all disabled:opacity-50 disabled:cursor-not-allowed text-left"
              >
                <div className="flex items-start gap-3">
                  {/* Checkbox */}
                  <div className="flex-shrink-0 mt-0.5">
                    {isCreating ? (
                      <div className="w-5 h-5 border-2 border-[#8B0000] rounded flex items-center justify-center">
                        <div className="w-3 h-3 border-2 border-t-transparent border-[#8B0000] rounded-full animate-spin" />
                      </div>
                    ) : (
                      <div className="w-5 h-5 border-2 border-[#666666] rounded hover:border-[#8B0000]" />
                    )}
                  </div>

                  {/* Content */}
                  <div className="flex-1">
                    <div className="font-medium text-white">
                      {suggestion.title}
                    </div>
                    {suggestion.description && (
                      <p className="text-xs text-[#CCCCCC] mt-1">
                        {suggestion.description}
                      </p>
                    )}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
        <div className="text-xs text-[#666666] mt-2 italic">
          Click any subtask to create it in your task list
        </div>
      </div>
    );
  };

  // T073: Render pattern insights
  const renderPatternInsights = () => {
    if (!patternInsights || patternInsights.length === 0) {
      return null;
    }

    return (
      <div className="mt-3 space-y-2">
        <div className="text-xs text-[#999999] font-semibold mb-2">
          Pattern Insights:
        </div>
        <div className="space-y-3">
          {patternInsights.map((insight, index) => (
            <div
              key={index}
              className="bg-[#2A2A2A] border border-[#444444] rounded-lg p-3 text-sm"
            >
              <div className="flex items-start gap-2">
                {/* Icon based on pattern type */}
                <div className="flex-shrink-0 mt-0.5">
                  <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                    />
                  </svg>
                </div>

                <div className="flex-1">
                  {/* Pattern type badge */}
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs px-2 py-0.5 rounded bg-blue-900/30 text-blue-400 font-semibold">
                      {insight.pattern_type}
                    </span>
                    {insight.frequency && (
                      <span className="text-xs text-[#999999]">
                        {insight.frequency}x
                      </span>
                    )}
                  </div>

                  {/* Description */}
                  <p className="text-white mb-1">
                    {insight.description}
                  </p>

                  {/* Examples */}
                  {insight.examples && insight.examples.length > 0 && (
                    <div className="mt-2">
                      <div className="text-xs text-[#999999] mb-1">Examples:</div>
                      <ul className="list-disc list-inside space-y-0.5">
                        {insight.examples.map((example, exIdx) => (
                          <li key={exIdx} className="text-xs text-[#CCCCCC]">
                            {example}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div
      className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}
    >
      <div
        className={`${hasQueryResults || hasSubtaskSuggestions || hasPatternInsights ? "max-w-[90%]" : "max-w-[80%]"} rounded-lg px-4 py-3 ${
          isUser
            ? "bg-[#8B0000] text-white"
            : isSystem
            ? "bg-[#2A2A2A] text-[#CCCCCC] border border-[#444444]"
            : "bg-[#1A1A1A] text-white border border-[#333333]"
        }`}
      >
        {/* Message content */}
        <div className="text-sm leading-relaxed whitespace-pre-wrap break-words">
          {message.content}
        </div>

        {/* T057: Query results display */}
        {renderQueryResults()}

        {/* T070: Subtask suggestions display */}
        {renderSubtaskSuggestions()}

        {/* T073: Pattern insights display */}
        {renderPatternInsights()}

        {/* Timestamp */}
        <div
          className={`text-xs mt-2 ${
            isUser ? "text-white/70" : "text-gray-400"
          }`}
        >
          {new Date(message.created_at).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </div>
      </div>
    </div>
  );
}
