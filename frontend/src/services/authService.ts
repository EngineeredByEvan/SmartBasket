import axios from 'axios';
import { LoginCredentials, RegisterData, User } from '../types';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export const login = async (credentials: LoginCredentials) => {
  const params = new URLSearchParams();
  params.append('username', credentials.username);
  params.append('password', credentials.password);

  const response = await axios.post('http://localhost:8000/token', params, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });

  const token = response.data.access_token;

  localStorage.setItem('token', token);

  const user = await getCurrentUser();

  return { token, user };
};

export const register = async (data: RegisterData) => {
  const { username, email, password } = data;

  const payload = { username, email, password };

  console.log("REGISTER PAYLOAD:", payload); // Add this line to confirm

  try {
    await axios.post(`${API}/users/`, payload);
  } catch (err) {
    if (axios.isAxiosError(err)) {
      console.error("Backend registration error:", err.response?.data || err.message);
    } else {
      console.error("Unknown error during registration:", err);
    }
    throw err;
  }
  

  const { token, user } = await login({ username, password });
  return { token, user };
};



export const getCurrentUser = async (): Promise<User> => {
  const token = localStorage.getItem('token');
  const response = await axios.get(`${API}/users/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
};

export const getAuthHeader = async () => {
  const token = localStorage.getItem('token');
  return {
    Authorization: `Bearer ${token}`,
  };
};
