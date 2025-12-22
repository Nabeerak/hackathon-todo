// T035: Create ChatInput.tsx component with text input, send button, keyboard submit (Enter key)
// T084: Support ref forwarding for keyboard shortcut focus
// Phase 3 - User Story 1: Natural Language Task Creation

"use client";

import { useState, KeyboardEvent, forwardRef } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

const ChatInput = forwardRef<HTMLInputElement, ChatInputProps>(
  function ChatInput({ onSend, disabled = false, placeholder = "Type a message..." }, ref) {
    const [input, setInput] = useState("");

  const handleSend = () => {
    const trimmedInput = input.trim();
    if (trimmedInput && !disabled) {
      onSend(trimmedInput);
      setInput("");
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex items-center gap-2 p-3 border-t border-[#333333] bg-[#1A1A1A]">
      <input
        ref={ref}
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        className="flex-1 px-3 py-2 bg-[#2A2A2A] text-white border border-[#444444] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#8B0000] focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed text-sm"
      />
      <button
        onClick={handleSend}
        disabled={disabled || !input.trim()}
        className="px-4 py-2 bg-[#8B0000] text-white rounded-lg hover:bg-[#A01010] transition-colors disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-[#8B0000] font-medium text-sm"
        aria-label="Send message"
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
            d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
          />
        </svg>
      </button>
    </div>
  );
});

export default ChatInput;
