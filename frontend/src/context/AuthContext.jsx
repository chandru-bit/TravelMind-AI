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
      const res = await api.post('/auth/login', { email, password });
      const { access_token, user: userData } = res.data;
      setToken(access_token);
      setUser(userData);
      localStorage.setItem('travelmind_token', access_token);
      localStorage.setItem('travelmind_user', JSON.stringify(userData));
      return { success: true };
    } catch (err) {
      return { success: false, message: err.userFriendlyMessage || 'Login failed.' };
    } finally {
      setLoading(false);
    }
  };

  const register = async (name, email, password) => {
    setLoading(true);
    try {
      const res = await api.post('/auth/register', { name, email, password });
      const { access_token, user: userData } = res.data;
      setToken(access_token);
      setUser(userData);
      localStorage.setItem('travelmind_token', access_token);
      localStorage.setItem('travelmind_user', JSON.stringify(userData));
      return { success: true };
    } catch (err) {
      return { success: false, message: err.userFriendlyMessage || 'Registration failed.' };
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

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, setUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
