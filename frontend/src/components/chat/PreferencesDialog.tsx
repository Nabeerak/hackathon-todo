// T092: Create PreferencesDialog.tsx in frontend/components/chat/ to display/edit AI tone, language, proactive suggestions toggle
// Phase 7 - User Story 5: AI Learning & Personalization

"use client";

import { useState, useEffect } from "react";
import type { UserPreferences, AITone } from "@/types/chat";

interface PreferencesDialogProps {
  /** Whether dialog is open */
  isOpen: boolean;
  /** Callback when dialog should close */
  onClose: () => void;
  /** Current user preferences */
  preferences: UserPreferences | null;
  /** Callback when preferences are saved */
  onSave: (preferences: Partial<UserPreferences>) => Promise<void>;
  /** Whether save operation is in progress */
  isSaving?: boolean;
}

/**
 * PreferencesDialog component for managing AI assistant settings.
 * Allows users to customize AI tone, language, and proactive suggestions.
 */
export default function PreferencesDialog({
  isOpen,
  onClose,
  preferences,
  onSave,
  isSaving = false,
}: PreferencesDialogProps) {
  // Local state for form fields
  const [aiTone, setAiTone] = useState<AITone>("professional");
  const [preferredLanguage, setPreferredLanguage] = useState("en");
  const [enableProactiveSuggestions, setEnableProactiveSuggestions] = useState(false);
  const [aisFeaturesEnabled, setAiFeaturesEnabled] = useState(true);

  // Initialize form fields when preferences change
  useEffect(() => {
    if (preferences) {
      setAiTone(preferences.ai_tone);
      setPreferredLanguage(preferences.preferred_language);
      setEnableProactiveSuggestions(preferences.enable_proactive_suggestions);
      setAiFeaturesEnabled(preferences.ai_features_enabled);
    }
  }, [preferences]);

  const handleSave = async () => {
    const updatedPreferences: Partial<UserPreferences> = {
      ai_tone: aiTone,
      preferred_language: preferredLanguage,
      enable_proactive_suggestions: enableProactiveSuggestions,
      ai_features_enabled: aisFeaturesEnabled,
    };

    await onSave(updatedPreferences);
  };

  const handleCancel = () => {
    // Reset to original values
    if (preferences) {
      setAiTone(preferences.ai_tone);
      setPreferredLanguage(preferences.preferred_language);
      setEnableProactiveSuggestions(preferences.enable_proactive_suggestions);
      setAiFeaturesEnabled(preferences.ai_features_enabled);
    }
    onClose();
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-50"
        onClick={handleCancel}
      />

      {/* Dialog */}
      <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
        <div className="bg-[#1A1A1A] border border-[#333333] rounded-lg shadow-2xl max-w-md w-full">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-[#333333]">
            <h2 className="text-xl font-semibold text-white">AI Preferences</h2>
            <button
              onClick={handleCancel}
              className="text-[#CCCCCC] hover:text-white transition-colors"
              aria-label="Close dialog"
            >
              <svg
                className="w-5 h-5"
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
            {/* AI Features Toggle */}
            <div className="flex items-center justify-between">
              <div>
                <label htmlFor="ai-features" className="text-white font-medium block">
                  Enable AI Features
                </label>
                <p className="text-[#AAAAAA] text-sm mt-1">
                  Master toggle for all AI assistant functionality
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  id="ai-features"
                  type="checkbox"
                  checked={aisFeaturesEnabled}
                  onChange={(e) => setAiFeaturesEnabled(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-[#333333] peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-[#8B0000] rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#8B0000]"></div>
              </label>
            </div>

            {/* AI Tone */}
            <div>
              <label htmlFor="ai-tone" className="text-white font-medium block mb-2">
                AI Tone
              </label>
              <select
                id="ai-tone"
                value={aiTone}
                onChange={(e) => setAiTone(e.target.value as AITone)}
                disabled={!aisFeaturesEnabled}
                className="w-full bg-[#0A0A0A] border border-[#333333] text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#8B0000] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option value="professional">Professional</option>
                <option value="casual">Casual</option>
                <option value="concise">Concise</option>
              </select>
              <p className="text-[#AAAAAA] text-sm mt-2">
                {aiTone === "professional" && "Formal and detailed responses"}
                {aiTone === "casual" && "Friendly and conversational responses"}
                {aiTone === "concise" && "Brief and to-the-point responses"}
              </p>
            </div>

            {/* Preferred Language */}
            <div>
              <label htmlFor="language" className="text-white font-medium block mb-2">
                Language
              </label>
              <select
                id="language"
                value={preferredLanguage}
                onChange={(e) => setPreferredLanguage(e.target.value)}
                disabled={!aisFeaturesEnabled}
                className="w-full bg-[#0A0A0A] border border-[#333333] text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#8B0000] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
                <option value="de">German</option>
                <option value="ja">Japanese</option>
                <option value="zh">Chinese</option>
              </select>
              <p className="text-[#AAAAAA] text-sm mt-2">
                AI will respond in your preferred language
              </p>
            </div>

            {/* Proactive Suggestions */}
            <div className="flex items-center justify-between">
              <div>
                <label htmlFor="proactive" className="text-white font-medium block">
                  Proactive Suggestions
                </label>
                <p className="text-[#AAAAAA] text-sm mt-1">
                  AI suggests actions without prompting (e.g., overdue task reminders)
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  id="proactive"
                  type="checkbox"
                  checked={enableProactiveSuggestions}
                  onChange={(e) => setEnableProactiveSuggestions(e.target.checked)}
                  disabled={!aisFeaturesEnabled}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-[#333333] peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-[#8B0000] rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#8B0000] peer-disabled:opacity-50"></div>
              </label>
            </div>
          </div>

          {/* Footer */}
          <div className="flex justify-end gap-3 p-6 border-t border-[#333333]">
            <button
              onClick={handleCancel}
              disabled={isSaving}
              className="px-4 py-2 text-[#CCCCCC] hover:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="px-4 py-2 bg-[#8B0000] text-white rounded-lg hover:bg-[#A01010] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isSaving && (
                <svg
                  className="animate-spin h-4 w-4"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
              )}
              {isSaving ? "Saving..." : "Save"}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
