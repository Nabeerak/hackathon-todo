// T018: TypeScript types for Task and User entities

export interface User {
  id: string;
  email: string;
  display_name: string | null;
  created_at: string;
}

export interface Task {
  id: number;
  user_id: number;
  title: string;
  description: string | null;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  display_name?: string;
}

export interface SigninRequest {
  email: string;
  password: string;
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
}

export interface ApiError {
  detail: string;
  status_code?: number;
}
