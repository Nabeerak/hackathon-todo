/**
 * Phase 3: AI Chat Client
 * Client for real-time chat communication with the AI backend.
 * T039: Implement ChatClient.sendMessage() with JWT auth
 * T040: Implement ChatClient.confirmAction() to POST to /api/v1/ai/actions/{id}/confirm
 */

import type { ChatMessageResponse, ActionConfirmResponse } from "@/types/chat";
import { TokenManager } from "./api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * ChatClient class for managing chat communication with the AI backend.
 *
 * @example
 * const client = new ChatClient();
 * const response = await client.sendMessage("Add buy groceries tomorrow");
 * if (response.action) {
 *   await client.confirmAction(response.action.id);
 * }
 */
export class ChatClient {
  private getHeaders(includeAuth: boolean = true): HeadersInit {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    };

    if (includeAuth) {
      const token = TokenManager.getToken();
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }
    }

    return headers;
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      let errorMessage = "An error occurred";
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch {
        errorMessage = `Error: ${response.statusText}`;
      }

      // Handle specific error codes
      if (response.status === 503) {
        throw new Error("AI assistant is temporarily unavailable. Please try again later or use the traditional form.");
      }

      if (response.status === 401 || response.status === 403) {
        throw new Error("Authentication failed. Please sign in again.");
      }

      throw new Error(errorMessage);
    }

    return response.json();
  }

  /**
   * Send a message to the AI chat endpoint.
   * T039: Implementation with JWT auth
   *
   * @param message - User's natural language message
   * @returns Promise resolving to AI response with proposed actions
   */
  async sendMessage(message: string): Promise<ChatMessageResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/messages`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ content: message }),
    });

    return this.handleResponse<ChatMessageResponse>(response);
  }

  /**
   * Confirm a proposed task action.
   * T040: Implementation to POST to /api/v1/ai/actions/{id}/confirm
   *
   * @param actionId - ID of the TaskAction to confirm
   * @returns Promise resolving to execution result with created/updated task
   */
  async confirmAction(actionId: string): Promise<ActionConfirmResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/ai/actions/${actionId}/confirm`, {
      method: "POST",
      headers: this.getHeaders(),
    });

    return this.handleResponse<ActionConfirmResponse>(response);
  }

  /**
   * Reject a proposed task action.
   *
   * @param actionId - ID of the TaskAction to reject
   * @returns Promise resolving to rejection confirmation
   *
   * @stub Implementation in Phase 3 (US2)
   */
  async rejectAction(actionId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/v1/ai/actions/${actionId}/reject`, {
      method: "POST",
      headers: this.getHeaders(),
    });

    await this.handleResponse<void>(response);
  }

  /**
   * Get user AI preferences.
   * T094: Implementation to GET from /api/v1/ai/preferences
   *
   * @returns Promise resolving to user preferences
   */
  async getPreferences(): Promise<UserPreferences> {
    const response = await fetch(`${API_BASE_URL}/api/v1/ai/preferences`, {
      method: "GET",
      headers: this.getHeaders(),
    });

    return this.handleResponse<UserPreferences>(response);
  }

  /**
   * Update user AI preferences.
   * T094: Implementation to PATCH to /api/v1/ai/preferences
   *
   * @param updates - Preference fields to update
   * @returns Promise resolving to updated preferences
   */
  async updatePreferences(updates: Partial<UserPreferences>): Promise<UserPreferences> {
    const response = await fetch(`${API_BASE_URL}/api/v1/ai/preferences`, {
      method: "PATCH",
      headers: this.getHeaders(),
      body: JSON.stringify(updates),
    });

    return this.handleResponse<UserPreferences>(response);
  }

  /**
   * Get AI quota information.
   * T097: Implementation to GET from /api/v1/ai/quota
   *
   * @param period - "day" or "hour"
   * @returns Promise resolving to quota information
   */
  async getQuota(period: "day" | "hour" = "day"): Promise<QuotaResponse> {
    const response = await fetch(`${API_BASE_URL}/api/v1/ai/quota?period=${period}`, {
      method: "GET",
      headers: this.getHeaders(),
    });

    return this.handleResponse<QuotaResponse>(response);
  }
}

/**
 * User preferences interface for AI customization
 */
export interface UserPreferences {
  user_id: number;
  preferred_language: string;
  ai_tone: "professional" | "casual" | "concise";
  enable_proactive_suggestions: boolean;
  ai_features_enabled: boolean;
  learned_shortcuts: Record<string, any>;
  created_at: string;
  updated_at: string;
}

/**
 * Quota information interface
 */
export interface QuotaResponse {
  user_id: number;
  period: "day" | "hour";
  limit: number;
  remaining: number;
  resets_at: string;
  cost_to_date: number;
}
