// T047: Create TaskList component to display all tasks
// T054: Display empty state message when no tasks exist
// T090: Make task list layout responsive (grid/stack)

"use client";

import type { Task } from "@/types/task";
import TaskItem from "./TaskItem";

interface TaskListProps {
  tasks: Task[];
  onToggleComplete: (taskId: string) => Promise<void>;
  onEdit: (task: Task) => void;
  onDelete: (taskId: string) => Promise<void>;
  onAddTask?: () => void;
}

export default function TaskList({ tasks, onToggleComplete, onEdit, onDelete, onAddTask }: TaskListProps) {
  if (tasks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 px-6">
        {/* Icon */}
        <div className="flex items-center justify-center rounded-full bg-[var(--card)] border-2 border-dashed mb-8" style={{
          borderColor: 'rgba(139, 0, 0, 0.4)',
          width: '160px',
          height: '160px'
        }}>
          <svg
            className="w-20 h-20"
            fill="none"
            stroke="url(#iconGradient)"
            viewBox="0 0 24 24"
            strokeWidth={2.5}
          >
            <defs>
              <linearGradient id="iconGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style={{ stopColor: '#8B0000', stopOpacity: 1 }} />
                <stop offset="50%" style={{ stopColor: '#FF4500', stopOpacity: 0.9 }} />
                <stop offset="100%" style={{ stopColor: '#FFD700', stopOpacity: 0.85 }} />
              </linearGradient>
            </defs>
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
        </div>

        {/* Heading */}
        <h3 className="text-3xl font-bold mb-5 text-center" style={{ color: '#FFFFFF' }}>
          No tasks yet
        </h3>

        {/* Description */}
        <p className="text-lg max-w-xl text-center leading-relaxed mb-10" style={{ color: '#CCCCCC', lineHeight: '1.8' }}>
          Start by creating your first task to get organized and stay productive.
        </p>

        {/* Button */}
        {onAddTask && (
          <button
            onClick={onAddTask}
            className="px-10 py-4 rounded-lg transition-all duration-200 inline-flex items-center justify-center gap-3 font-bold shadow-lg text-lg"
            style={{
              background: '#8B0000',
              color: '#FFFFFF',
              boxShadow: '0 4px 20px 0 rgba(139, 0, 0, 0.6)',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#A01010';
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 8px 25px 0 rgba(139, 0, 0, 0.8)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = '#8B0000';
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 20px 0 rgba(139, 0, 0, 0.6)';
            }}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            Create Your First Task
          </button>
        )}
      </div>
    );
  }

  // Separate completed and pending tasks
  const pendingTasks = tasks.filter((task) => !task.is_completed);
  const completedTasks = tasks.filter((task) => task.is_completed);

  return (
    <div className="space-y-8">
      {/* Pending Tasks */}
      {pendingTasks.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-[var(--foreground)] opacity-70 px-1">
            Pending ({pendingTasks.length})
          </h2>
          <div className="space-y-3">
            {pendingTasks.map((task) => (
              <TaskItem
                key={task.id}
                task={task}
                onToggleComplete={onToggleComplete}
                onEdit={onEdit}
                onDelete={onDelete}
              />
            ))}
          </div>
        </div>
      )}

      {/* Completed Tasks */}
      {completedTasks.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-[var(--foreground)] opacity-70 px-1">
            Completed ({completedTasks.length})
          </h2>
          <div className="space-y-3">
            {completedTasks.map((task) => (
              <TaskItem
                key={task.id}
                task={task}
                onToggleComplete={onToggleComplete}
                onEdit={onEdit}
                onDelete={onDelete}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
