import React, { createContext, useContext, useEffect, useState } from 'react';
import { AuthState, User, LoginCredentials, RegisterData } from '../types';
import * as authService from '../services/authService';

interface AuthContextProps extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  getCurrentUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextProps | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  const isAuthenticated = !!user;

  const login = async (credentials: LoginCredentials) => {
    const { token, user } = await authService.login(credentials);
    localStorage.setItem('token', token);
    setToken(token);
    setUser(user);
  };

  const register = async (data: RegisterData) => {
    const { token, user } = await authService.register(data);
    localStorage.setItem('token', token);
    setToken(token);
    setUser(user);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  const getCurrentUser = async () => {
    try {
      if (!token) {
        setUser(null);
        return;
      }
      const user = await authService.getCurrentUser();
      setUser(user);
    } catch (err) {
      logout(); // token invalid or user fetch failed
    }
  };

  useEffect(() => {
    const init = async () => {
      if (token) {
        try {
          const user = await authService.getCurrentUser();
          setUser(user);
        } catch {
          logout();
        }
      }
      setLoading(false);
    };
  
    init();
  }, [token]);
  

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated,
        loading,
        login,
        register,
        logout,
        getCurrentUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextProps => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
