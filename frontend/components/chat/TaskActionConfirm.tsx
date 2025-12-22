// T038: Create TaskActionConfirm.tsx dialog component with Confirm/Reject buttons
// T058: Update TaskActionConfirm.tsx to handle different action types with action-specific messaging
// T060: Add Reject button to TaskActionConfirm dialog (already implemented)
// T063: Handle ambiguous commands - show multiple task matches for user selection
// Phase 3 - User Story 1 & 2: Natural Language Task Creation & Conversational Task Management

"use client";

import type { TaskAction } from "@/types/chat";

interface TaskActionConfirmProps {
  action: TaskAction;
  onConfirm: () => void;
  onReject: () => void;
  isProcessing?: boolean;
}

export default function TaskActionConfirm({
  action,
  onConfirm,
  onReject,
  isProcessing = false,
}: TaskActionConfirmProps) {
  // T058: Enhanced action descriptions for different action types
  const getActionDescription = () => {
    switch (action.action_type) {
      case "create":
        return "I'll create a new task with these details:";
      case "update":
        return "I'll update the task with these changes:";
      case "delete":
        return "Are you sure you want to delete this task?";
      case "complete":
        return "I'll mark this task as complete:";
      case "query":
        return "I'll search for tasks matching these criteria:";
      default:
        return "I'll perform this action:";
    }
  };

  const getActionTitle = () => {
    switch (action.action_type) {
      case "create":
        return "Create Task";
      case "update":
        return "Update Task";
      case "delete":
        return "Delete Task";
      case "complete":
        return "Complete Task";
      case "query":
        return "Query Tasks";
      default:
        return "Confirm Action";
    }
  };

  const getConfirmButtonText = () => {
    switch (action.action_type) {
      case "create":
        return "Create";
      case "update":
        return "Update";
      case "delete":
        return "Delete";
      case "complete":
        return "Mark Complete";
      case "query":
        return "Search";
      default:
        return "Confirm";
    }
  };

  // T058: Enhanced parameter rendering for different action types
  const renderExtractedParams = () => {
    const params = action.extracted_params;
    if (!params || Object.keys(params).length === 0) {
      return null;
    }

    // T063: Handle multiple task matches for ambiguous commands
    if (params.matched_tasks && Array.isArray(params.matched_tasks) && params.matched_tasks.length > 1) {
      return (
        <div className="mt-3 space-y-2">
          <div className="text-xs text-[#999999] mb-2">
            Multiple tasks found. Which one did you mean?
          </div>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {params.matched_tasks.map((task: any, index: number) => (
              <div
                key={task.id || index}
                className="bg-[#1A1A1A] border border-[#555555] rounded p-2 hover:border-[#8B0000] cursor-pointer transition-colors"
              >
                <div className="flex items-center gap-2">
                  <div
                    className={`w-2 h-2 rounded-full ${
                      task.is_completed ? "bg-green-500" : "bg-yellow-500"
                    }`}
                  />
                  <span className="text-sm text-white font-medium">{task.title}</span>
                </div>
                {task.description && (
                  <p className="text-xs text-[#CCCCCC] mt-1 ml-4 truncate">
                    {task.description}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      );
    }

    return (
      <div className="mt-3 space-y-2">
        {params.task_id && (
          <div>
            <span className="text-xs text-[#999999]">Task ID:</span>
            <p className="text-sm text-white font-medium">#{params.task_id}</p>
          </div>
        )}
        {params.task_title && (
          <div>
            <span className="text-xs text-[#999999]">Current Title:</span>
            <p className="text-sm text-white font-medium">{params.task_title}</p>
          </div>
        )}
        {params.title && (
          <div>
            <span className="text-xs text-[#999999]">
              {action.action_type === "update" ? "New Title:" : "Title:"}
            </span>
            <p className="text-sm text-white font-medium">{params.title}</p>
          </div>
        )}
        {params.description && (
          <div>
            <span className="text-xs text-[#999999]">
              {action.action_type === "update" ? "New Description:" : "Description:"}
            </span>
            <p className="text-sm text-[#CCCCCC]">{params.description}</p>
          </div>
        )}
        {params.due_date && (
          <div>
            <span className="text-xs text-[#999999]">Due date:</span>
            <p className="text-sm text-[#CCCCCC]">
              {new Date(params.due_date).toLocaleDateString()}
            </p>
          </div>
        )}
        {params.priority && (
          <div>
            <span className="text-xs text-[#999999]">Priority:</span>
            <p className="text-sm text-[#CCCCCC] capitalize">
              {params.priority}
            </p>
          </div>
        )}
        {params.is_completed !== undefined && (
          <div>
            <span className="text-xs text-[#999999]">Status:</span>
            <p className="text-sm text-[#CCCCCC]">
              {params.is_completed ? "Completed" : "Pending"}
            </p>
          </div>
        )}
        {params.filters && (
          <div>
            <span className="text-xs text-[#999999]">Search Criteria:</span>
            <p className="text-sm text-[#CCCCCC]">{JSON.stringify(params.filters, null, 2)}</p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-[#1A1A1A] border border-[#333333] rounded-lg max-w-md w-full p-6 shadow-xl">
        {/* Header */}
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-white mb-1">
            {getActionTitle()}
          </h3>
          <p className="text-sm text-[#CCCCCC]">
            {getActionDescription()}
          </p>
        </div>

        {/* Action details */}
        <div className="bg-[#2A2A2A] border border-[#444444] rounded-lg p-4 mb-4">
          {renderExtractedParams()}

          {/* Confidence score */}
          {action.confidence_score && (
            <div className="mt-3 pt-3 border-t border-[#444444]">
              <div className="flex items-center justify-between">
                <span className="text-xs text-[#999999]">AI Confidence:</span>
                <span className="text-xs text-[#CCCCCC]">
                  {Math.round(action.confidence_score * 100)}%
                </span>
              </div>
              <div className="mt-1 w-full bg-[#1A1A1A] rounded-full h-1.5">
                <div
                  className="bg-[#8B0000] h-1.5 rounded-full transition-all"
                  style={{ width: `${action.confidence_score * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Action buttons */}
        <div className="flex gap-3">
          <button
            onClick={onReject}
            disabled={isProcessing}
            className="flex-1 px-4 py-2 bg-[#2A2A2A] text-white border border-[#444444] rounded-lg hover:bg-[#333333] transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium text-sm"
          >
            Reject
          </button>
          <button
            onClick={onConfirm}
            disabled={isProcessing}
            className="flex-1 px-4 py-2 bg-[#8B0000] text-white rounded-lg hover:bg-[#A01010] transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium text-sm"
          >
            {isProcessing ? "Processing..." : getConfirmButtonText()}
          </button>
        </div>
      </div>
    </div>
  );
}
