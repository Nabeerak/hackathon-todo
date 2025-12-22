/**
 * Quota warning component for ChatWidget
 * T097: Display quota warning when user approaches limit
 */

'use client';

import React from 'react';
import type { QuotaInfo } from '../../types/chat';

interface QuotaWarningProps {
  quota: QuotaInfo | null;
  loading?: boolean;
}

export function QuotaWarning({ quota, loading }: QuotaWarningProps) {
  if (loading || !quota) {
    return null;
  }

  const { remaining_requests, limit, used } = quota;
  const percentUsed = (used / limit) * 100;

  // Show warning when less than 20 requests remaining or >80% used
  const showWarning = remaining_requests < 20 || percentUsed > 80;

  if (!showWarning) {
    return null;
  }

  // Determine severity
  const isUrgent = remaining_requests < 10 || percentUsed > 90;

  return (
    <div
      className={`px-3 py-2 rounded-md text-sm mb-2 ${
        isUrgent
          ? 'bg-red-50 border border-red-200 text-red-800'
          : 'bg-yellow-50 border border-yellow-200 text-yellow-800'
      }`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="font-semibold">
            {isUrgent ? '⚠️' : '💡'}
          </span>
          <span>
            {remaining_requests} AI request{remaining_requests !== 1 ? 's' : ''} remaining today
          </span>
        </div>
        <span className="text-xs opacity-75">
          {used}/{limit}
        </span>
      </div>
      {isUrgent && (
        <p className="mt-1 text-xs">
          You're running low on AI requests. Consider using the traditional form for simple tasks.
        </p>
      )}
    </div>
  );
}
