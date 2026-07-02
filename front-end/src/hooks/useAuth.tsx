import React, { createContext, useContext, useEffect } from 'react';
import { useAuthStore } from '@/core/auth/auth.store';
import type { Role } from '@/core/auth/auth.types';

interface AuthContextType {
  role: Role;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { role, login, logout, isAuthenticated, isLoading, initialize } = useAuthStore();

  useEffect(() => {
    initialize();

    // Global session expiration handler
    const handleSessionExpired = () => {
      useAuthStore.getState().logout();
    };

    window.addEventListener('auth_session_expired', handleSessionExpired);
    return () => {
      window.removeEventListener('auth_session_expired', handleSessionExpired);
    };
  }, [initialize]);

  return (
    <AuthContext.Provider value={{ role, login, logout, isAuthenticated, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  
  // If used outside provider, fallback gracefully to store hook
  if (context === undefined) {
    const { role, login, logout, isAuthenticated, isLoading } = useAuthStore();
    return { role, login, logout, isAuthenticated, isLoading };
  }
  
  return context;
};
