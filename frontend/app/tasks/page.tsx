// T046: Create main task list page with authentication guard
// T052: Fetch and display user's task list on page load
// T055: Add loading and error states for API calls
// T062: Update local state optimistically on completion toggle
// T071: Add onPlanTask handler to open chat with pre-filled message
// T081: Update local state after successful edit
// T088: Remove task from local state after successful deletion
// T041: Add ChatWidget to frontend/src/app/tasks/page.tsx with lazy loading
// T044: Refresh task list after successful task creation via chat

"use client";

import { useState, useEffect, lazy, Suspense } from "react";
import { useRouter } from "next/navigation";
import { apiClient, TokenManager } from "@/lib/api";
import { AuthService } from "@/lib/auth";
import type { Task } from "@/types/task";
import Header from "@/components/Header";
import TaskList from "@/components/TaskList";
import TaskForm from "@/components/TaskForm";
import Spinner from "@/components/ui/Spinner";

// T041: Lazy load ChatWidget for better performance
const ChatWidget = lazy(() => import("@/components/chat/ChatWidget"));

export default function TasksPage() {
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  // T071: State for pre-filled chat message
  const [chatInitialMessage, setChatInitialMessage] = useState<string | undefined>(undefined);

  // Authentication guard - redirect to signin if not authenticated
  useEffect(() => {
    if (!AuthService.isAuthenticated()) {
      router.push("/auth/signin");
      return;
    }

    // Fetch tasks on mount
    fetchTasks();
  }, [router]);

  const fetchTasks = async () => {
    const userId = TokenManager.getUserId();
    const token = TokenManager.getToken();

    console.log("Fetching tasks for user:", userId);
    console.log("Has token:", !!token);

    if (!userId) {
      console.error("No user ID found in localStorage");
      router.push("/auth/signin");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const fetchedTasks = await apiClient.getTasks(userId);
      console.log("Tasks fetched successfully:", fetchedTasks.length);
      setTasks(fetchedTasks);
    } catch (err) {
      console.error("Failed to fetch tasks:", err);
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateTask = async (data: { title: string; description: string }) => {
    const userId = TokenManager.getUserId();
    if (!userId) return;

    console.log("Creating task for user:", userId);

    try {
      const newTask = await apiClient.createTask(userId, {
        title: data.title,
        description: data.description || undefined,
      });
      console.log("Task created:", newTask);
      setTasks((prev) => [newTask, ...prev]);
      setShowForm(false);
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : "Failed to create task");
    }
  };

  const handleUpdateTask = async (data: { title: string; description: string }) => {
    const userId = TokenManager.getUserId();
    if (!userId || !editingTask) return;

    try {
      const updatedTask = await apiClient.updateTask(userId, editingTask.id, {
        title: data.title,
        description: data.description || undefined,
      });

      // T081: Update local state after successful edit
      setTasks((prev) => prev.map((task) => (task.id === updatedTask.id ? updatedTask : task)));
      setEditingTask(null);
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : "Failed to update task");
    }
  };

  const handleToggleComplete = async (taskId: number) => {
    const userId = TokenManager.getUserId();
    if (!userId) return;

    // T062: Optimistic update
    const taskToUpdate = tasks.find((t) => t.id === taskId);
    if (taskToUpdate) {
      setTasks((prev) =>
        prev.map((task) => (task.id === taskId ? { ...task, is_completed: !task.is_completed } : task))
      );
    }

    try {
      const updatedTask = await apiClient.toggleTaskCompletion(userId, taskId);
      // Update with server response
      setTasks((prev) => prev.map((task) => (task.id === updatedTask.id ? updatedTask : task)));
    } catch (err) {
      // Revert optimistic update on error
      if (taskToUpdate) {
        setTasks((prev) =>
          prev.map((task) => (task.id === taskId ? taskToUpdate : task))
        );
      }
      throw new Error(err instanceof Error ? err.message : "Failed to toggle task completion");
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    const userId = TokenManager.getUserId();
    if (!userId) return;

    console.log("Attempting to delete task:", { userId, taskId });

    // Find the task in local state to verify ownership
    const taskToDelete = tasks.find((t) => t.id === taskId);
    if (taskToDelete) {
      console.log("Task found in local state:", taskToDelete);
    }

    try {
      await apiClient.deleteTask(userId, taskId);
      console.log("Task deleted successfully:", taskId);
      // T088: Remove task from local state after successful deletion
      setTasks((prev) => prev.filter((task) => task.id !== taskId));
    } catch (err) {
      console.error("Delete task error:", err);
      throw new Error(err instanceof Error ? err.message : "Failed to delete task");
    }
  };

  const handleEdit = (task: Task) => {
    setEditingTask(task);
    setShowForm(false);
  };

  const handleCancelEdit = () => {
    setEditingTask(null);
  };

  const handleAddTask = () => {
    setEditingTask(null);
    setShowForm(true);
  };

  const handleCancelCreate = () => {
    setShowForm(false);
  };

  // T071: Handle "Help me plan this task" button click
  const handlePlanTask = (task: Task) => {
    const message = `Help me plan this task: "${task.title}". ${task.description ? `Description: ${task.description}` : ""}`;
    setChatInitialMessage(message);
    // Reset after a short delay to allow re-triggering
    setTimeout(() => setChatInitialMessage(undefined), 1000);
  };

  if (isLoading) {
    return (
      <>
        <Header />
        <div className="min-h-screen pt-[70px] flex items-center justify-center">
          <div className="text-center space-y-6">
            <Spinner size="lg" />
            <p className="text-lg font-medium" style={{ color: '#CCCCCC' }}>Loading your tasks...</p>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Header />
      <div className={`min-h-screen bg-[var(--background)] pt-[70px] ${tasks.length === 0 ? 'flex items-center justify-center' : ''}`}>
        <div className="container mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 w-full py-6">
          {/* Page header - Only show when tasks exist */}
          {tasks.length > 0 && (
            <div className="mb-12 text-center">
              <h1 className="text-3xl sm:text-4xl font-bold mb-3" style={{ color: '#FFFFFF' }}>My Tasks</h1>
              <p className="text-base sm:text-lg" style={{ color: '#CCCCCC' }}>
                Manage your tasks and stay organized
              </p>
            </div>
          )}

          {/* Error state */}
          {error && (
            <div className="mb-6 p-4 rounded-lg border max-w-2xl mx-auto" style={{
              backgroundColor: 'rgba(139, 0, 0, 0.15)',
              borderColor: 'rgba(139, 0, 0, 0.5)',
              color: '#FFB3B3'
            }}>
              <p className="font-medium">{error}</p>
              <button
                onClick={fetchTasks}
                className="mt-2 text-sm underline hover:no-underline transition-colors"
                style={{ color: '#FFFFFF' }}
                onMouseEnter={(e) => e.currentTarget.style.color = '#FFD700'}
                onMouseLeave={(e) => e.currentTarget.style.color = '#FFFFFF'}
              >
                Try again
              </button>
            </div>
          )}

          {/* Add task button (only show when tasks exist and not creating/editing) */}
          {!showForm && !editingTask && tasks.length > 0 && (
            <div className="mb-8 flex justify-center">
              <button
                onClick={handleAddTask}
                className="px-8 py-3 rounded-lg transition-all duration-200 flex items-center justify-center gap-2 font-semibold text-base shadow-lg"
                style={{
                  background: '#8B0000',
                  color: '#FFFFFF',
                  boxShadow: '0 4px 14px 0 rgba(139, 0, 0, 0.5)',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = '#A01010';
                  e.currentTarget.style.boxShadow = '0 6px 20px 0 rgba(139, 0, 0, 0.7)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = '#8B0000';
                  e.currentTarget.style.boxShadow = '0 4px 14px 0 rgba(139, 0, 0, 0.5)';
                }}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                </svg>
                Add Task
              </button>
            </div>
          )}

          {/* Task creation form */}
          {showForm && (
            <div className="mb-8 max-w-2xl mx-auto">
              <div className="mb-4 text-center">
                <h2 className="text-xl font-semibold" style={{ color: '#FFFFFF' }}>Create New Task</h2>
              </div>
              <TaskForm onSubmit={handleCreateTask} onCancel={handleCancelCreate} />
            </div>
          )}

          {/* Task editing form */}
          {editingTask && (
            <div className="mb-8 max-w-2xl mx-auto">
              <div className="mb-4 text-center">
                <h2 className="text-xl font-semibold" style={{ color: '#FFFFFF' }}>Edit Task</h2>
              </div>
              <TaskForm
                onSubmit={handleUpdateTask}
                onCancel={handleCancelEdit}
                initialData={editingTask}
                isEditing
              />
            </div>
          )}

          {/* Task list */}
          <TaskList
            tasks={tasks}
            onToggleComplete={handleToggleComplete}
            onEdit={handleEdit}
            onDelete={handleDeleteTask}
            onAddTask={handleAddTask}
            onPlanTask={handlePlanTask}
          />
        </div>

        {/* T041: ChatWidget with lazy loading */}
        {/* T044: Pass fetchTasks to refresh list after chat task creation */}
        {/* T071: Pass initialMessage to pre-fill chat */}
        <Suspense fallback={null}>
          <ChatWidget onTaskCreated={fetchTasks} initialMessage={chatInitialMessage} />
        </Suspense>
      </div>
    </>
  );
}
