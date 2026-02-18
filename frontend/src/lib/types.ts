// User types
export interface User {
  id: number;
  email: string;
  created_at: string;
}

// Auth types
export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface UserRegister {
  email: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

// Task types
export interface Task {
  id: number;
  user_id: number;
  title: string;
  description: string | null;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  is_completed?: boolean;
}

export interface TaskList {
  tasks: Task[];
  total: number;
}

// Error types
export interface ErrorResponse {
  detail: string;
}
