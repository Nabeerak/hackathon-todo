/**
 * Task action confirmation dialog
 */

'use client';

import React from 'react';
import type { TaskAction } from '../../types/chat';

interface TaskActionConfirmProps {
  action: TaskAction;
  onConfirm: () => void;
  onReject: () => void;
  loading?: boolean;
}

export function TaskActionConfirm({ action, onConfirm, onReject, loading }: TaskActionConfirmProps) {
  const renderActionDetails = () => {
    const params = action.extracted_params;

    switch (action.action_type) {
      case 'create':
        return (
          <div className="space-y-2">
            <div>
              <span className="font-semibold">Title:</span> {params.title}
            </div>
            {params.description && (
              <div>
                <span className="font-semibold">Description:</span> {params.description}
              </div>
            )}
            {params.dueDate && (
              <div>
                <span className="font-semibold">Due Date:</span> {params.dueDate}
              </div>
            )}
            {params.priority && (
              <div>
                <span className="font-semibold">Priority:</span> {params.priority}
              </div>
            )}
          </div>
        );

      case 'update':
        return (
          <div className="space-y-2">
            <div>
              <span className="font-semibold">Target:</span> {params.target || 'Selected task'}
            </div>
            {params.title && (
              <div>
                <span className="font-semibold">New Title:</span> {params.title}
              </div>
            )}
            {params.description && (
              <div>
                <span className="font-semibold">New Description:</span> {params.description}
              </div>
            )}
          </div>
        );

      case 'complete':
        return (
          <div>
            <span className="font-semibold">Task:</span> {params.target || 'Selected task'}
          </div>
        );

      case 'delete':
        return (
          <div>
            <span className="font-semibold">Target:</span>{' '}
            {params.bulkCriteria ? `All tasks matching: ${params.bulkCriteria}` : params.target || 'Selected task'}
          </div>
        );

      case 'query':
        return (
          <div>
            <span className="font-semibold">Filter:</span>{' '}
            {JSON.stringify(params.filters || {}, null, 2)}
          </div>
        );

      default:
        return <div>Action details: {JSON.stringify(params, null, 2)}</div>;
    }
  };

  const getActionTitle = () => {
    switch (action.action_type) {
      case 'create':
        return 'Create Task';
      case 'update':
        return 'Update Task';
      case 'complete':
        return 'Complete Task';
      case 'delete':
        return 'Delete Task';
      case 'query':
        return 'Query Tasks';
      default:
        return 'Confirm Action';
    }
  };

  return (
    <div className="border-t bg-blue-50 p-4">
      <h4 className="font-semibold text-blue-900 mb-3">{getActionTitle()}</h4>
      <div className="text-sm text-blue-800 mb-4">{renderActionDetails()}</div>
      {action.confidence_score !== undefined && (
        <div className="text-xs text-blue-600 mb-3">
          Confidence: {Math.round(action.confidence_score * 100)}%
        </div>
      )}
      <div className="flex gap-2">
        <button
          onClick={onConfirm}
          disabled={loading}
          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? 'Confirming...' : 'Confirm'}
        </button>
        <button
          onClick={onReject}
          disabled={loading}
          className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:bg-gray-100 disabled:cursor-not-allowed transition-colors"
        >
          Reject
        </button>
      </div>
    </div>
  );
}
