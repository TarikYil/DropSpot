import React, { createContext, useState, useContext, useEffect } from 'react';
import { authService } from '../services/api';
import { setAuthToken, removeAuthToken, getAuthToken } from '../utils/auth';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = getAuthToken();
    if (token) {
      try {
        const response = await authService.me();
        setUser(response.data);
      } catch (error) {
        removeAuthToken();
        setUser(null);
      }
    }
    setLoading(false);
  };

  const login = async (username, password) => {
    try {
      const response = await authService.login({ username, password });
      const { access_token, refresh_token } = response.data;
      setAuthToken(access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      const userResponse = await authService.me();
      setUser(userResponse.data);
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Giriş başarısız' 
      };
    }
  };

  const register = async (userData) => {
    try {
      await authService.register(userData);
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Kayıt başarısız' 
      };
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      removeAuthToken();
      localStorage.removeItem('refresh_token');
      setUser(null);
    }
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
    isAdmin: user?.is_superuser || false,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

