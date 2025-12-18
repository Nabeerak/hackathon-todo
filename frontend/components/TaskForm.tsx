// T049: Create TaskForm component for create/edit
// T050: Implement task creation form with title and description fields
// T051: Integrate create task API call with form submission
// T053: Add client-side validation (title required, length limits)
// T077: Implement edit mode in TaskForm component
// T078: Pre-populate form with existing task data for editing
// T079: Implement cancel edit functionality to revert changes
// T080: Integrate update task API call
// T091: Make task form responsive with appropriate input sizing

"use client";

import { useState, useEffect } from "react";
import type { Task } from "@/types/task";

interface TaskFormProps {
  onSubmit: (data: { title: string; description: string }) => Promise<void>;
  onCancel?: () => void;
  initialData?: Task | null;
  isEditing?: boolean;
}

export default function TaskForm({ onSubmit, onCancel, initialData, isEditing = false }: TaskFormProps) {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
  });
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Pre-populate form with existing data when editing
  useEffect(() => {
    if (isEditing && initialData) {
      setFormData({
        title: initialData.title,
        description: initialData.description || "",
      });
    } else {
      setFormData({
        title: "",
        description: "",
      });
    }
  }, [isEditing, initialData]);

  const validateForm = (): boolean => {
    const newErrors: { [key: string]: string } = {};

    // Title validation
    if (!formData.title.trim()) {
      newErrors.title = "Title is required";
    } else if (formData.title.length > 200) {
      newErrors.title = "Title must be 200 characters or less";
    }

    // Description validation
    if (formData.description && formData.description.length > 1000) {
      newErrors.description = "Description must be 1000 characters or less";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit({
        title: formData.title.trim(),
        description: formData.description.trim(),
      });

      // Reset form after successful creation (not edit)
      if (!isEditing) {
        setFormData({ title: "", description: "" });
      }
    } catch (error) {
      console.error("Form submission error:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    }
    setFormData({ title: "", description: "" });
    setErrors({});
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: "" }));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 sm:p-6 bg-[var(--card)] border border-[var(--border)] rounded-lg">
      <div className="space-y-4">
        <div>
          <label htmlFor="title" className="block text-sm font-medium mb-1">
            Title *
          </label>
          <input
            id="title"
            name="title"
            type="text"
            required
            value={formData.title}
            onChange={handleChange}
            maxLength={200}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--primary)] bg-[var(--background)] text-base ${
              errors.title ? "border-red-500" : "border-[var(--border)]"
            }`}
            placeholder="Enter task title"
          />
          <div className="flex justify-between items-center mt-1">
            {errors.title && <p className="text-sm text-red-600 dark:text-red-400">{errors.title}</p>}
            <p className="text-xs text-[var(--foreground)] opacity-60 ml-auto">
              {formData.title.length}/200
            </p>
          </div>
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium mb-1">
            Description (optional)
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            maxLength={1000}
            rows={3}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--primary)] bg-[var(--background)] resize-none text-base ${
              errors.description ? "border-red-500" : "border-[var(--border)]"
            }`}
            placeholder="Add more details about your task"
          />
          <div className="flex justify-between items-center mt-1">
            {errors.description && <p className="text-sm text-red-600 dark:text-red-400">{errors.description}</p>}
            <p className="text-xs text-[var(--foreground)] opacity-60 ml-auto">
              {formData.description.length}/1000
            </p>
          </div>
        </div>
      </div>

      <div className="flex flex-col-reverse sm:flex-row gap-2 sm:gap-3 justify-end">
        {(isEditing || onCancel) && (
          <button
            type="button"
            onClick={handleCancel}
            disabled={isSubmitting}
            className="w-full sm:w-auto px-4 py-2 rounded-lg border border-[var(--border)] hover:bg-[var(--background)] transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={isSubmitting || !formData.title.trim()}
          className="w-full sm:w-auto px-4 py-2 rounded-lg bg-[var(--primary)] text-white hover:bg-[var(--primary-hover)] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? (isEditing ? "Updating..." : "Creating...") : isEditing ? "Update Task" : "Add Task"}
        </button>
      </div>
    </form>
  );
}
