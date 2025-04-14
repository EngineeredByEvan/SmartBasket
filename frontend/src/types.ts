// User related types
export interface User {
    id: number;
    username: string;
    email: string;
    role: 'user' | 'admin';
    is_active: boolean;
    created_at: string;
  }
  
  export interface LoginCredentials {
    username: string;
    password: string;
  }
  
  export interface RegisterData {
    username: string;
    email: string;
    password: string;
    confirmPassword?: string;
  }
  
  export interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    loading: boolean;
  }

  export interface AuthResponse {
    token: string;
    user: User;
  }
  
  
  // Prediction related types
  export interface PredictionItem {
    item: string;
    probability: number;
  }
  
  export interface Prediction {
    basket: string[];
    predicted_items: PredictionItem[];
    timestamp: string;
  }
  
  export interface PredictionLog {
    id: number;
    user_id: number;
    timestamp: string;
    input_data: string[];
    output_data: string[];
    probabilities: number[];
    feedback?: string;
  }
  
  // Transaction related types
  export interface Transaction {
    id: number;
    user_id: number;
    date: string;
    items: string[];
  }
  
  export interface TransactionCreate {
    date?: string;
    items: string[];
  }
  
  // Model related types
  export interface ModelMetrics {
    accuracy: number;
    top3_accuracy: number;
    top5_accuracy: number;
    [key: string]: any;
  }
  
  export interface ModelDeployment {
    id: number;
    model_version: string;
    deployed_by: number;
    deployment_time: string;
    status: string;
    metrics: ModelMetrics;
  }
  
  export interface ModelDeploymentCreate {
    model_version: string;
    metrics: ModelMetrics;
  }