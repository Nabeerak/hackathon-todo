/**
 * Phase 3 - User Story 4: Multi-Modal Task Interaction
 * T081: Implement SSE client using @microsoft/fetch-event-source
 *
 * SSE (Server-Sent Events) client for real-time task updates.
 * Connects to /api/v1/chat/stream endpoint for bidirectional sync
 * between traditional UI and AI chat.
 */

import { fetchEventSource } from "@microsoft/fetch-event-source";
import { TokenManager } from "./api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * SSE Event types emitted by the backend
 */
export type SSEEventType = "task_created" | "task_updated" | "task_deleted" | "task_completed";

/**
 * SSE Event data structure
 */
export interface SSEEvent {
  /** Event type */
  event_type: SSEEventType;
  /** Task data */
  task?: any;
  /** Task ID for delete events */
  task_id?: string;
  /** User ID for ownership validation */
  user_id: string;
  /** Timestamp of the event */
  timestamp: string;
}

/**
 * SSE Event handler callback type
 */
export type SSEEventHandler = (event: SSEEvent) => void;

/**
 * SSE Connection state
 */
export type SSEConnectionState = "connecting" | "connected" | "disconnected" | "error";

/**
 * SSE Client for real-time task updates
 *
 * @example
 * const sseClient = new SSEClient();
 *
 * sseClient.on('task_created', (event) => {
 *   console.log('New task created:', event.task);
 * });
 *
 * await sseClient.connect();
 */
export class SSEClient {
  private eventHandlers: Map<SSEEventType | "all", SSEEventHandler[]> = new Map();
  private abortController: AbortController | null = null;
  private connectionState: SSEConnectionState = "disconnected";
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private maxReconnectDelay = 30000; // Max 30 seconds
  private visibilityHandler: (() => void) | null = null;
  private shouldAutoReconnect = true;

  /**
   * Register an event handler for specific event types
   *
   * @param eventType - Event type to listen for, or "all" for all events
   * @param handler - Callback function to handle the event
   */
  on(eventType: SSEEventType | "all", handler: SSEEventHandler): void {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, []);
    }
    this.eventHandlers.get(eventType)?.push(handler);
  }

  /**
   * Unregister an event handler
   *
   * @param eventType - Event type to stop listening for
   * @param handler - The handler function to remove
   */
  off(eventType: SSEEventType | "all", handler: SSEEventHandler): void {
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  /**
   * Emit an event to all registered handlers
   *
   * @param event - The SSE event to emit
   */
  private emit(event: SSEEvent): void {
    // Call specific event handlers
    const specificHandlers = this.eventHandlers.get(event.event_type);
    specificHandlers?.forEach((handler) => handler(event));

    // Call "all" event handlers
    const allHandlers = this.eventHandlers.get("all");
    allHandlers?.forEach((handler) => handler(event));
  }

  /**
   * Get current connection state
   */
  getState(): SSEConnectionState {
    return this.connectionState;
  }

  /**
   * Set up page visibility change handler to manage connection
   */
  private setupVisibilityHandler(): void {
    if (this.visibilityHandler) {
      return; // Already set up
    }

    this.visibilityHandler = () => {
      if (document.hidden) {
        console.debug("Tab hidden - SSE connection will be maintained");
        // Note: We don't disconnect on hidden anymore to maintain real-time updates
        // The browser may throttle, but we keep the connection alive
      } else {
        console.debug("Tab visible - checking SSE connection");
        // Reconnect if disconnected while tab was hidden
        if (this.connectionState === "disconnected" && this.shouldAutoReconnect) {
          console.log("Reconnecting SSE after tab became visible");
          this.connect().catch((err) => {
            console.error("Failed to reconnect after visibility change:", err);
          });
        }
      }
    };

    if (typeof document !== "undefined") {
      document.addEventListener("visibilitychange", this.visibilityHandler);
    }
  }

  /**
   * Remove page visibility change handler
   */
  private removeVisibilityHandler(): void {
    if (this.visibilityHandler && typeof document !== "undefined") {
      document.removeEventListener("visibilitychange", this.visibilityHandler);
      this.visibilityHandler = null;
    }
  }

  /**
   * Connect to the SSE endpoint
   *
   * @returns Promise that resolves when connection is established
   */
  async connect(): Promise<void> {
    if (this.connectionState === "connected" || this.connectionState === "connecting") {
      console.warn("SSE client already connecting or connected");
      return;
    }

    const token = TokenManager.getToken();
    if (!token) {
      console.error("No authentication token found. Cannot connect to SSE.");
      this.connectionState = "error";
      throw new Error("Authentication required for SSE connection");
    }

    this.abortController = new AbortController();
    this.connectionState = "connecting";
    this.shouldAutoReconnect = true;

    // Set up visibility handler to manage reconnections
    this.setupVisibilityHandler();

    const url = `${API_BASE_URL}/api/v1/chat/stream`;

    try {
      await fetchEventSource(url, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Accept": "text/event-stream",
        },
        signal: this.abortController.signal,

        onopen: async (response) => {
          if (response.ok) {
            console.log("SSE connection established");
            this.connectionState = "connected";
            this.reconnectAttempts = 0;
            this.reconnectDelay = 1000; // Reset delay
            return;
          }

          // Handle authentication errors
          if (response.status === 401 || response.status === 403) {
            console.error("SSE authentication failed");
            this.connectionState = "error";
            throw new Error("Authentication failed");
          }

          // Handle other errors
          console.error("SSE connection failed:", response.status, response.statusText);
          this.connectionState = "error";
          throw new Error(`Connection failed: ${response.statusText}`);
        },

        onmessage: (event) => {
          // Skip empty or whitespace-only messages
          if (!event.data || !event.data.trim()) {
            console.debug("Received empty SSE message, ignoring");
            return;
          }

          // Ignore heartbeat/keep-alive messages
          if (event.data === "ping" || event.data === "heartbeat") {
            return;
          }

          try {
            const data = JSON.parse(event.data);

            // Handle connection confirmation event (sent by backend on connect)
            if (data.user_id && data.timestamp && !data.event_type) {
              console.log("SSE connection confirmed for user:", data.user_id);
              return;
            }

            // Handle task events
            if (data.event_type) {
              console.log("SSE event received:", data.event_type, data);
              this.emit(data as SSEEvent);
            } else {
              console.warn("Received SSE message with unknown format:", data);
            }
          } catch (error) {
            console.error("Failed to parse SSE event:", error);
            console.error("Raw event data:", event.data);
          }
        },

        onerror: (error) => {
          // Check if this is an AbortError from visibility change
          const isAbortError = error instanceof Error && error.name === "AbortError";

          if (isAbortError) {
            console.debug("SSE connection aborted (likely due to tab visibility change)");
            this.connectionState = "disconnected";
            // Don't attempt reconnection for abort errors - visibility handler will manage this
            return;
          }

          console.error("SSE connection error:", error);
          this.connectionState = "error";

          // Attempt reconnection with exponential backoff
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = Math.min(
              this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
              this.maxReconnectDelay
            );

            console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

            setTimeout(() => {
              this.connect().catch((err) => {
                console.error("Reconnection failed:", err);
              });
            }, delay);
          } else {
            console.error("Max reconnection attempts reached. Giving up.");
            this.connectionState = "disconnected";
          }

          // Don't throw - let the library handle retries
          throw error;
        },

        onclose: () => {
          console.log("SSE connection closed");
          this.connectionState = "disconnected";
        },
      });
    } catch (error) {
      // Handle AbortError from visibility changes gracefully
      if (error instanceof Error && error.name === "AbortError") {
        console.debug("SSE connection aborted");
        this.connectionState = "disconnected";
        return; // Don't throw for abort errors
      }

      console.error("SSE connection setup failed:", error);
      this.connectionState = "error";
      throw error;
    }
  }

  /**
   * Disconnect from the SSE endpoint
   */
  disconnect(): void {
    this.shouldAutoReconnect = false; // Prevent automatic reconnection

    if (this.abortController) {
      console.log("Disconnecting SSE client");
      this.abortController.abort();
      this.abortController = null;
    }

    this.connectionState = "disconnected";
    this.reconnectAttempts = 0;

    // Clean up visibility handler
    this.removeVisibilityHandler();
  }

  /**
   * Check if client is currently connected
   */
  isConnected(): boolean {
    return this.connectionState === "connected";
  }
}

/**
 * Singleton SSE client instance
 * Use this instance to maintain a single connection across the application
 */
let sseClientInstance: SSEClient | null = null;

/**
 * Get the singleton SSE client instance
 *
 * @returns The global SSE client instance
 */
export function getSSEClient(): SSEClient {
  if (!sseClientInstance) {
    sseClientInstance = new SSEClient();
  }
  return sseClientInstance;
}
