// T017: API client with JWT token handling
// T069: Add JWT token to all API request headers
// T070: Redirect to signin page when authentication fails
// T071: Handle 401/403 errors gracefully with user feedback
// T098: Add user-friendly error messages for all validation failures

import type {
  Task,
  User,
  AuthTokens,
  SignupRequest,
  SigninRequest,
  CreateTaskRequest,
  UpdateTaskRequest,
  ApiError,
} from "@/types/task";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Token management
export const TokenManager = {
  getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("access_token");
  },

  setToken(token: string): void {
    if (typeof window === "undefined") return;
    localStorage.setItem("access_token", token);
  },

  removeToken(): void {
    if (typeof window === "undefined") return;
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_id");
    localStorage.removeItem("user_email");
  },

  getUserId(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("user_id");
  },

  setUserId(userId: string): void {
    if (typeof window === "undefined") return;
    localStorage.setItem("user_id", userId);
  },

  getUserEmail(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("user_email");
  },

  setUserEmail(email: string): void {
    if (typeof window === "undefined") return;
    localStorage.setItem("user_email", email);
  },
};

// T097: Implement consistent error response format
class ApiClient {
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      let errorMessage = "An error occurred";
      try {
        const errorData: ApiError = await response.json();
        errorMessage = errorData.detail || errorMessage;
      } catch {
        errorMessage = `Error: ${response.statusText}`;
      }

      // T071: Handle 401/403 errors gracefully
      if (response.status === 401 || response.status === 403) {
        console.warn("Authentication error:", errorMessage);

        // Only clear token and redirect for actual auth failures
        // Don't do this during initial load or if it's a transient error
        const shouldLogout = errorMessage.includes("Invalid or expired token") ||
                            errorMessage.includes("token") ||
                            errorMessage.includes("Unauthorized");

        if (shouldLogout) {
          TokenManager.removeToken();
          // T070: Redirect to signin page when authentication fails
          if (typeof window !== "undefined") {
            // Delay slightly to avoid race conditions
            setTimeout(() => {
              window.location.href = "/auth/signin?error=session_expired";
            }, 500);
          }
        }
        throw new Error(errorMessage);
      }

      throw new Error(errorMessage);
    }

    // Handle 204 No Content - has no response body by HTTP spec
    if (response.status === 204) {
      return {} as T;
    }

    // Check content type and body existence before parsing
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
      // Clone response to check if body is empty without consuming it
      const text = await response.text();
      if (text.length === 0) {
        return {} as T;
      }
      return JSON.parse(text) as T;
    }

    return {} as T;
  }

  private getHeaders(includeAuth: boolean = false): HeadersInit {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    };

    // T069: Add JWT token to all API request headers
    if (includeAuth) {
      const token = TokenManager.getToken();
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }
    }

    return headers;
  }

  // Authentication endpoints
  async signup(data: SignupRequest): Promise<AuthTokens & { user?: User }> {
    const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });

    const result = await this.handleResponse<AuthTokens & { user?: User }>(response);

    // Store token and user info after successful signup
    if (result.access_token) {
      TokenManager.setToken(result.access_token);
      TokenManager.setUserEmail(data.email);

      // Extract and store user ID from the response (backend sends it in response.user.id)
      if (result.user?.id) {
        TokenManager.setUserId(String(result.user.id));
        console.log("User signed up successfully. User ID:", result.user.id);
      } else {
        // Fallback: Decode JWT to get user ID if not provided in response
        try {
          const payload = JSON.parse(atob(result.access_token.split('.')[1]));
          const userId = payload.sub || payload.user_id || payload.id;
          if (userId) {
            TokenManager.setUserId(String(userId));
            console.log("User signed up successfully. User ID (from token):", userId);
          }
        } catch (e) {
          console.error("Failed to decode token:", e);
        }
      }
    }

    return result;
  }

  async signin(data: SigninRequest): Promise<AuthTokens & { user?: User }> {
    const response = await fetch(`${API_BASE_URL}/api/auth/signin`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });

    const result = await this.handleResponse<AuthTokens & { user?: User }>(response);

    // Store token and user info after successful signin
    if (result.access_token) {
      TokenManager.setToken(result.access_token);
      TokenManager.setUserEmail(data.email);

      // Extract and store user ID from the response (backend sends it in response.user.id)
      if (result.user?.id) {
        TokenManager.setUserId(String(result.user.id));
        console.log("User signed in successfully. User ID:", result.user.id);
      } else {
        // Fallback: Decode JWT to get user ID if not provided in response
        try {
          const payload = JSON.parse(atob(result.access_token.split('.')[1]));
          const userId = payload.sub || payload.user_id || payload.id;
          if (userId) {
            TokenManager.setUserId(String(userId));
            console.log("User signed in successfully. User ID (from token):", userId);
          }
        } catch (e) {
          console.error("Failed to decode token:", e);
        }
      }
    }

    return result;
  }

  async signout(): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/auth/signout`, {
      method: "POST",
      headers: this.getHeaders(true),
    });

    await this.handleResponse<void>(response);
    TokenManager.removeToken();
  }

  // Task endpoints
  async getTasks(userId: string | number): Promise<Task[]> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks`, {
      method: "GET",
      headers: this.getHeaders(true),
    });

    return this.handleResponse<Task[]>(response);
  }

  async getTask(userId: string | number, taskId: string | number): Promise<Task> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks/${taskId}`, {
      method: "GET",
      headers: this.getHeaders(true),
    });

    return this.handleResponse<Task>(response);
  }

  async createTask(userId: string | number, data: CreateTaskRequest): Promise<Task> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks`, {
      method: "POST",
      headers: this.getHeaders(true),
      body: JSON.stringify(data),
    });

    return this.handleResponse<Task>(response);
  }

  async updateTask(userId: string | number, taskId: string | number, data: UpdateTaskRequest): Promise<Task> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks/${taskId}`, {
      method: "PUT",
      headers: this.getHeaders(true),
      body: JSON.stringify(data),
    });

    return this.handleResponse<Task>(response);
  }

  async toggleTaskCompletion(userId: string | number, taskId: string | number): Promise<Task> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks/${taskId}/complete`, {
      method: "PATCH",
      headers: this.getHeaders(true),
    });

    return this.handleResponse<Task>(response);
  }

  async deleteTask(userId: string | number, taskId: string | number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/${userId}/tasks/${taskId}`, {
      method: "DELETE",
      headers: this.getHeaders(true),
    });

    return this.handleResponse<void>(response);
  }
}

export const apiClient = new ApiClient();
