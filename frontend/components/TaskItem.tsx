// T048: Create TaskItem component to render individual task
// T059: Add completion checkbox/button to TaskItem component
// T060: Implement toggle completion API call
// T061: Add visual distinction for completed vs pending tasks
// T076: Add edit button to TaskItem component
// T085: Add delete button to TaskItem component
// T086: Implement confirmation dialog for task deletion
// T092: Ensure touch-friendly buttons and checkboxes on mobile

"use client";

import { useState } from "react";
import type { Task } from "@/types/task";

interface TaskItemProps {
  task: Task;
  onToggleComplete: (taskId: string) => Promise<void>;
  onEdit: (task: Task) => void;
  onDelete: (taskId: string) => Promise<void>;
}

export default function TaskItem({ task, onToggleComplete, onEdit, onDelete }: TaskItemProps) {
  const [isTogglingComplete, setIsTogglingComplete] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const handleToggleComplete = async () => {
    if (isTogglingComplete) return;
    setIsTogglingComplete(true);
    try {
      await onToggleComplete(task.id);
    } finally {
      setIsTogglingComplete(false);
    }
  };

  const handleDelete = async () => {
    if (isDeleting) return;
    setIsDeleting(true);
    try {
      await onDelete(task.id);
      setShowDeleteConfirm(false);
    } catch {
      setIsDeleting(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  };

  return (
    <>
      <div className="group p-4 bg-[var(--card)] border border-[var(--border)] rounded-lg hover:shadow-md transition-all">
        <div className="flex items-start gap-3">
          {/* Completion checkbox - touch-friendly */}
          <button
            onClick={handleToggleComplete}
            disabled={isTogglingComplete}
            className="flex-shrink-0 mt-0.5 w-6 h-6 sm:w-5 sm:h-5 rounded border-2 border-[var(--primary)] flex items-center justify-center hover:bg-[var(--primary)] hover:bg-opacity-10 transition-colors disabled:opacity-50"
            aria-label={task.is_completed ? "Mark as incomplete" : "Mark as complete"}
          >
            {task.is_completed && (
              <svg className="w-4 h-4 sm:w-3.5 sm:h-3.5 text-[var(--primary)]" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            )}
          </button>

          {/* Task content */}
          <div className="flex-1 min-w-0">
            <h3
              className={`text-base sm:text-lg font-medium break-words ${
                task.is_completed ? "line-through text-[var(--foreground)] opacity-50" : ""
              }`}
            >
              {task.title}
            </h3>
            {task.description && (
              <p
                className={`mt-1 text-sm text-[var(--foreground)] opacity-70 break-words ${
                  task.is_completed ? "line-through opacity-40" : ""
                }`}
              >
                {task.description}
              </p>
            )}
            <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-[var(--foreground)] opacity-60">
              <span>Created: {formatDate(task.created_at)}</span>
              {task.updated_at !== task.created_at && (
                <>
                  <span>•</span>
                  <span>Updated: {formatDate(task.updated_at)}</span>
                </>
              )}
            </div>
          </div>

          {/* Action buttons - touch-friendly */}
          <div className="flex-shrink-0 flex gap-2">
            <button
              onClick={() => onEdit(task)}
              className="p-2 text-[var(--primary)] hover:bg-[var(--primary)] hover:bg-opacity-10 rounded-lg transition-colors"
              aria-label="Edit task"
              title="Edit task"
            >
              <svg className="w-5 h-5 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
            </button>
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="p-2 text-[var(--danger)] hover:bg-[var(--danger)] hover:bg-opacity-10 rounded-lg transition-colors"
              aria-label="Delete task"
              title="Delete task"
            >
              <svg className="w-5 h-5 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Delete confirmation dialog */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-[var(--background)] rounded-lg shadow-xl max-w-md w-full p-6 space-y-4">
            <h3 className="text-lg font-semibold">Delete Task</h3>
            <p className="text-sm text-[var(--foreground)] opacity-70">
              Are you sure you want to delete "{task.title}"? This action cannot be undone.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                disabled={isDeleting}
                className="px-4 py-2 rounded-lg border border-[var(--border)] hover:bg-[var(--card)] transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className="px-4 py-2 rounded-lg bg-[var(--danger)] text-white hover:bg-[var(--danger-hover)] transition-colors disabled:opacity-50"
              >
                {isDeleting ? "Deleting..." : "Delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
