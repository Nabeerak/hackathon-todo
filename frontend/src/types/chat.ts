/**
 * TypeScript interfaces for AI chat features
 */

export interface ChatMessage {
  id: string;
  user_id: number;
  session_id: string;
  content: string;
  message_type: 'user_message' | 'ai_response' | 'system_notification';
  created_at: string;
  metadata?: Record<string, any>;
}

export interface ChatSession {
  id: string;
  user_id: number;
  started_at: string;
  last_activity_at: string;
  is_active: boolean;
  context_summary?: string;
  message_count: number;
}

export interface TaskAction {
  action_id: string;
  action_type: 'create' | 'query' | 'update' | 'complete' | 'delete';
  extracted_params: Record<string, any>;
  confidence_score?: number;
  created_at: string;
  confirmation_status: 'pending' | 'confirmed' | 'rejected';
  executed_status: 'not_executed' | 'executing' | 'success' | 'failed';
  task?: any;
  error?: string;
}

export interface QuotaInfo {
  remaining_requests: number;
  resets_at: string;
  cost_to_date: number;
  period: string;
  limit: number;
  used: number;
}

export interface SendMessageRequest {
  content: string;
  session_id?: string;
}

export interface SendMessageResponse {
  session_id: string;
  user_message: ChatMessage;
  ai_response: ChatMessage;
  proposed_action?: TaskAction;
}

export interface ConfirmActionResponse {
  action_id: string;
  confirmation_status: string;
  executed_status: string;
  task?: any;
  error?: string;
}
