// T016: Setup Better Auth client configuration
// T037: Add session persistence and automatic token refresh

"use client";

import { TokenManager } from "./api";

export interface AuthState {
  isAuthenticated: boolean;
  userId: string | null;
  userEmail: string | null;
}

export const AuthService = {
  // Check if user is authenticated
  isAuthenticated(): boolean {
    if (typeof window === "undefined") return false;
    const token = TokenManager.getToken();
    return !!token;
  },

  // Get current authentication state
  getAuthState(): AuthState {
    if (typeof window === "undefined") {
      return {
        isAuthenticated: false,
        userId: null,
        userEmail: null,
      };
    }

    return {
      isAuthenticated: this.isAuthenticated(),
      userId: TokenManager.getUserId(),
      userEmail: TokenManager.getUserEmail(),
    };
  },

  // Redirect to signin if not authenticated
  requireAuth(): void {
    if (typeof window === "undefined") return;

    if (!this.isAuthenticated()) {
      window.location.href = "/auth/signin";
    }
  },

  // Redirect to tasks if already authenticated
  redirectIfAuthenticated(): void {
    if (typeof window === "undefined") return;

    if (this.isAuthenticated()) {
      window.location.href = "/tasks";
    }
  },
};
