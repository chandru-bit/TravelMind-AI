import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('travelmind_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem('travelmind_token') || null);
  const [loading, setLoading] = useState(false);

  const login = async (email, password) => {
    setLoading(true);
    try {
      const cleanEmail = (email || '').trim().toLowerCase();
      const res = await api.post('/auth/login', { email: cleanEmail, password });
      const { access_token, user: userData } = res.data;
      setToken(access_token);
      setUser(userData);
      localStorage.setItem('travelmind_token', access_token);
      localStorage.setItem('travelmind_user', JSON.stringify(userData));
      return { success: true };
    } catch (err) {
      const msg = err.userFriendlyMessage || 'Login failed. Please check your credentials.';
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  };

  const register = async (name, email, password) => {
    setLoading(true);
    try {
      const cleanEmail = (email || '').trim().toLowerCase();
      const res = await api.post('/auth/register', { name: name.trim(), email: cleanEmail, password });
      const { access_token, user: userData } = res.data;
      setToken(access_token);
      setUser(userData);
      localStorage.setItem('travelmind_token', access_token);
      localStorage.setItem('travelmind_user', JSON.stringify(userData));
      return { success: true };
    } catch (err) {
      const msg = err.userFriendlyMessage || 'Registration failed. Please try again.';
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('travelmind_token');
    localStorage.removeItem('travelmind_user');
  };

  const requestPasswordResetCode = async (email) => {
    setLoading(true);
    try {
      const res = await api.post('/auth/forgot-password', { email });
      return { success: true, message: res.data?.message, debug_code: res.data?.debug_code };
    } catch (err) {
      const msg = err.userFriendlyMessage || 'Failed to send reset code. Please check your email.';
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  };

  const resetPassword = async (email, code, newPassword) => {
    setLoading(true);
    try {
      const res = await api.post('/auth/reset-password', { email, code, new_password: newPassword });
      return { success: true, message: res.data?.message };
    } catch (err) {
      const msg = err.userFriendlyMessage || 'Password reset failed. Please verify your code and try again.';
      return { success: false, message: msg };
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, setUser, requestPasswordResetCode, resetPassword }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
