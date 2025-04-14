import axios from 'axios';
import { LoginCredentials, RegisterData, User } from '../types';

// Use the environment variable if it exists; otherwise default to your deployed URL.
const API_URL = process.env.REACT_APP_API_URL || 'https://smartbasket-u8bn.onrender.com/api/v1';
// The /token endpoint is located at the root (not under /api/v1), so we remove the suffix.
const TOKEN_URL = API_URL.replace('/api/v1', '');

export const login = async (credentials: LoginCredentials) => {
  const params = new URLSearchParams();
  params.append('username', credentials.username);
  params.append('password', credentials.password);

  // Send login to the token endpoint.
  const response = await axios.post(`${TOKEN_URL}/token`, params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });

  const token = response.data.access_token;
  localStorage.setItem('token', token);

  const user = await getCurrentUser();

  return { token, user };
};

export const register = async (data: RegisterData) => {
  // Create user via backend API (under /api/v1/users/)
  await axios.post(`${API_URL}/users/`, data);
  // Automatically log in after registration
  const { token, user } = await login({ username: data.username, password: data.password });
  return { token, user };
};

export const getCurrentUser = async (): Promise<User> => {
  const token = localStorage.getItem('token');
  const response = await axios.get(`${API_URL}/users/me`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.data;
};

export const getAuthHeader = async () => {
  const token = localStorage.getItem('token');
  return {
    Authorization: `Bearer ${token}`
  };
};
