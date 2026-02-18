'use client';

import React, { createContext, useState, useEffect, ReactNode } from 'react';
import apiClient from './api';
import { User, AuthResponse, UserLogin, UserRegister } from './types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (credentials: UserLogin) => Promise<void>;
  register: (userData: UserRegister) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing token on mount
    const token = localStorage.getItem('auth_token');
    if (token) {
      // Token exists, but we don't have user data
      // In a real app, you might validate the token or fetch user data
      setLoading(false);
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (credentials: UserLogin) => {
    try {
      const response = await apiClient.post<AuthResponse>('/auth/login', credentials);
      const { access_token, user: userData } = response.data;

      localStorage.setItem('auth_token', access_token);
      setUser(userData);
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  };

  const register = async (userData: UserRegister) => {
    try {
      const response = await apiClient.post<AuthResponse>('/auth/register', userData);
      const { access_token, user: newUser } = response.data;

      localStorage.setItem('auth_token', access_token);
      setUser(newUser);
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setUser(null);
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
