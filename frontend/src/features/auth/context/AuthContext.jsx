import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../../../lib/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(api.getToken());
  const [loading, setLoading] = useState(true);

  // Initialize and verify authentication on app load
  useEffect(() => {
    async function loadUser() {
      const storedToken = api.getToken();
      if (!storedToken) {
        setLoading(false);
        return;
      }
      try {
        const currentUser = await api.get('/auth/me');
        setUser(currentUser);
      } catch (err) {
        console.warn('Failed to load user session:', err.message);
        api.clearToken();
        setToken(null);
        setUser(null);
      } finally {
        setLoading(false);
      }
    }
    loadUser();
  }, []);

  const login = async (email, password) => {
    const data = await api.post('/auth/login', { email, password });
    api.setToken(data.access_token);
    setToken(data.access_token);
    setUser(data.user);
    return data.user;
  };

  const register = async (registerData) => {
    const newUser = await api.post('/auth/register', registerData);
    // After registration, auto-login the user
    return login(registerData.email, registerData.password);
  };

  const logout = async () => {
    try {
      if (token) {
        await api.post('/auth/logout', {});
      }
    } catch (e) {
      // Ignore network errors on logout
    } finally {
      api.clearToken();
      setToken(null);
      setUser(null);
    }
  };

  const updateProfile = async (profileData) => {
    const updated = await api.put('/auth/me', profileData);
    setUser(updated);
    return updated;
  };

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin',
    isStaff: user?.role === 'admin' || user?.role === 'staff',
    isCustomer: user?.role === 'customer',
    login,
    register,
    logout,
    updateProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
