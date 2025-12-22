// T092: Create PreferencesDialog.tsx component for AI preferences
// Phase 7 - User Story 5: AI Learning and Personalization

"use client";

import { useState, useEffect } from "react";
import type { UserPreferences } from "@/lib/chatClient";

interface PreferencesDialogProps {
  isOpen: boolean;
  onClose: () => void;
  preferences: UserPreferences | null;
  onSave: (updates: Partial<UserPreferences>) => Promise<void>;
  isSaving: boolean;
}

export default function PreferencesDialog({
  isOpen,
  onClose,
  preferences,
  onSave,
  isSaving,
}: PreferencesDialogProps) {
  const [aiTone, setAiTone] = useState<"professional" | "casual" | "concise">("professional");
  const [enableProactiveSuggestions, setEnableProactiveSuggestions] = useState(true);
  const [aiFeaturesEnabled, setAiFeaturesEnabled] = useState(true);

  // Update local state when preferences prop changes
  useEffect(() => {
    if (preferences) {
      setAiTone(preferences.ai_tone);
      setEnableProactiveSuggestions(preferences.enable_proactive_suggestions);
      setAiFeaturesEnabled(preferences.ai_features_enabled);
    }
  }, [preferences]);

  const handleSave = async () => {
    const updates: Partial<UserPreferences> = {
      ai_tone: aiTone,
      enable_proactive_suggestions: enableProactiveSuggestions,
      ai_features_enabled: aiFeaturesEnabled,
    };

    await onSave(updates);
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 z-50"
        onClick={onClose}
        aria-label="Close dialog"
      />

      {/* Dialog */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div
          className="bg-[#0A0A0A] border border-[#333333] rounded-lg shadow-2xl w-full max-w-md"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-[#333333]">
            <h2 className="text-xl font-semibold text-white">AI Preferences</h2>
            <button
              onClick={onClose}
              className="text-[#CCCCCC] hover:text-white transition-colors"
              aria-label="Close"
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
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* AI Tone */}
            <div>
              <label className="block text-sm font-medium text-[#CCCCCC] mb-2">
                AI Response Tone
              </label>
              <select
                value={aiTone}
                onChange={(e) => setAiTone(e.target.value as typeof aiTone)}
                className="w-full px-4 py-2 bg-[#1A1A1A] border border-[#333333] rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-[#8B0000] focus:border-transparent"
              >
                <option value="professional">Professional</option>
                <option value="casual">Casual</option>
                <option value="concise">Concise</option>
              </select>
              <p className="mt-1 text-xs text-[#999999]">
                {aiTone === "professional" && "Formal and detailed responses"}
                {aiTone === "casual" && "Friendly and conversational responses"}
                {aiTone === "concise" && "Brief and to-the-point responses"}
              </p>
            </div>

            {/* Proactive Suggestions */}
            <div>
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={enableProactiveSuggestions}
                  onChange={(e) => setEnableProactiveSuggestions(e.target.checked)}
                  className="w-4 h-4 text-[#8B0000] bg-[#1A1A1A] border-[#333333] rounded focus:ring-[#8B0000] focus:ring-2"
                />
                <span className="ml-3 text-sm font-medium text-[#CCCCCC]">
                  Enable Proactive Suggestions
                </span>
              </label>
              <p className="mt-1 ml-7 text-xs text-[#999999]">
                AI will suggest task breakdowns and offer help without being asked
              </p>
            </div>

            {/* AI Features Toggle */}
            <div>
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={aiFeaturesEnabled}
                  onChange={(e) => setAiFeaturesEnabled(e.target.checked)}
                  className="w-4 h-4 text-[#8B0000] bg-[#1A1A1A] border-[#333333] rounded focus:ring-[#8B0000] focus:ring-2"
                />
                <span className="ml-3 text-sm font-medium text-[#CCCCCC]">
                  Enable AI Features
                </span>
              </label>
              <p className="mt-1 ml-7 text-xs text-[#999999]">
                Master toggle for all AI functionality (you can still use traditional forms)
              </p>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 p-6 border-t border-[#333333]">
            <button
              onClick={onClose}
              disabled={isSaving}
              className="px-4 py-2 text-sm font-medium text-[#CCCCCC] hover:text-white transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="px-4 py-2 text-sm font-medium bg-[#8B0000] text-white rounded-lg hover:bg-[#A01010] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSaving ? "Saving..." : "Save Preferences"}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
