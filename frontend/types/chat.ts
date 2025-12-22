/**
 * Phase 3: AI Chat Type Definitions
 * TypeScript interfaces matching backend data model entities.
 */

/**
 * Message type enum
 */
export type MessageType = "user_message" | "ai_response" | "system_notification";

/**
 * Task action type enum
 */
export type ActionType = "create" | "update" | "delete" | "complete" | "query";

/**
 * Confirmation status enum
 */
export type ConfirmationStatus = "pending" | "confirmed" | "rejected";

/**
 * Execution status enum
 */
export type ExecutedStatus = "not_executed" | "executing" | "success" | "failed";

/**
 * AI tone preference enum
 */
export type AITone = "professional" | "casual" | "concise";

/**
 * ChatMessage entity
 * Represents a single message in the conversational AI interface.
 */
export interface ChatMessage {
  /** Unique message identifier */
  id: string;
  /** Owner of the message (for isolation) */
  user_id: string;
  /** Conversation session this message belongs to */
  session_id: string;
  /** Message text (user input or AI response) */
  content: string;
  /** Message type */
  message_type: MessageType;
  /** When message was created */
  created_at: string;
  /** Additional data (e.g., AI confidence score, token count) */
  metadata?: Record<string, any>;
}

/**
 * ChatSession entity
 * Represents a conversation session between user and AI assistant.
 */
export interface ChatSession {
  /** Unique session identifier */
  id: string;
  /** Session owner */
  user_id: string;
  /** When session was created */
  started_at: string;
  /** Last message timestamp */
  last_activity_at: string;
  /** Whether session is still ongoing */
  is_active: boolean;
  /** Compressed conversation context for long sessions */
  context_summary?: string;
  /** Total messages in session */
  message_count: number;
}

/**
 * TaskAction entity
 * Represents an AI-interpreted action on a task, pending confirmation or executed.
 */
export interface TaskAction {
  /** Unique action identifier */
  id: string;
  /** Session where action was proposed */
  session_id: string;
  /** Message that triggered this action */
  message_id: string;
  /** Action owner (for isolation) */
  user_id: string;
  /** Action type */
  action_type: ActionType;
  /** Structured parameters (e.g., {title, description, due_date}) */
  extracted_params: Record<string, any>;
  /** AI's confidence in interpretation (0.0-1.0) */
  confidence_score: number;
  /** Confirmation status */
  confirmation_status: ConfirmationStatus;
  /** Execution status */
  executed_status: ExecutedStatus;
  /** Related task (for update/delete/complete/query) */
  task_id?: string;
  /** Error details if execution failed */
  error_message?: string;
  /** When action was proposed */
  created_at: string;
  /** When user confirmed */
  confirmed_at?: string;
  /** When action was executed */
  executed_at?: string;
}

/**
 * UserPreferences entity
 * Stores AI personalization settings and learned user patterns.
 */
export interface UserPreferences {
  /** Unique preference record identifier */
  id: string;
  /** One preference record per user */
  user_id: string;
  /** AI response language */
  preferred_language: string;
  /** AI response tone */
  ai_tone: AITone;
  /** AI suggests actions without prompting */
  enable_proactive_suggestions: boolean;
  /** User-specific shortcuts */
  learned_shortcuts: Record<string, any>;
  /** Custom rate limit for premium users (requests/day) */
  rate_limit_override?: number;
  /** Master toggle for all AI features */
  ai_features_enabled: boolean;
  /** When preferences created */
  created_at: string;
  /** Last preference change */
  updated_at: string;
}

/**
 * AIContext entity
 * Maintains persistent context for AI interactions across sessions.
 */
export interface AIContext {
  /** Unique context record identifier */
  id: string;
  /** One context record per user */
  user_id: string;
  /** Key information from past sessions */
  conversation_summary?: string;
  /** Observed patterns */
  user_patterns: Record<string, any>;
  /** Lifetime message count */
  total_messages: number;
  /** Lifetime session count */
  total_sessions: number;
  /** Avg messages per session */
  average_session_length: number;
  /** Last context update */
  last_updated_at: string;
  /** When context created */
  created_at: string;
}

/**
 * API Response Types
 */

/** Response from POST /api/v1/chat/messages */
export interface ChatMessageResponse {
  /** Session ID */
  session_id: string;
  /** The user's message */
  user_message: ChatMessage;
  /** The AI's response message */
  ai_response: ChatMessage;
  /** Proposed action (if any) */
  proposed_action?: TaskAction;
}

/** Response from POST /api/v1/ai/actions/{id}/confirm */
export interface ActionConfirmResponse {
  /** Updated action with executed status */
  action: TaskAction;
  /** Created/updated task (if applicable) */
  task?: any; // TODO: Import Task type from task.ts
}

/** Response from GET /api/v1/ai/quota */
export interface QuotaResponse {
  /** User ID */
  user_id: string;
  /** Period (day or hour) */
  period: "day" | "hour";
  /** Request limit for period */
  limit: number;
  /** Remaining requests in period */
  remaining: number;
  /** When quota resets */
  resets_at: string;
  /** Total cost to date */
  cost_to_date: number;
}
