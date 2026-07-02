import { create } from 'zustand';
import { decodeToken, extractRoleFromToken } from './jwt.utils';
import { apiClient } from '../api/apiClient';
import type { Role } from './auth.types';

interface AuthState {
  token: string | null;
  role: Role | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  initialize: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  token: null,
  role: null,
  isAuthenticated: false,
  isLoading: true,

  initialize: () => {
    try {
      const token = localStorage.getItem('adhd_token');
      if (token) {
        const decoded = decodeToken(token);
        if (decoded && decoded.exp && decoded.exp * 1000 > Date.now()) {
          const extractedRole = extractRoleFromToken(decoded) as Role;
          set({
            token,
            role: extractedRole,
            isAuthenticated: true,
            isLoading: false
          });
          return;
        }
      }
    } catch (err) {
      console.error('Failed to initialize auth state:', err);
    }
    
    // Clear state if invalid or expired
    localStorage.removeItem('adhd_token');
    localStorage.removeItem('adhd_refresh_token');
    localStorage.removeItem('adhd_user');
    set({ token: null, role: null, isAuthenticated: false, isLoading: false });
  },

  login: async (email, password) => {
    set({ isLoading: true });
    try {
      const response = await apiClient.post<{ succeeded: boolean; data?: { token: string; refreshToken?: string }; message?: string }>(
        'Account/login', 
        { email, password }
      );

      if (response && response.succeeded && response.data?.token) {
        const token = response.data.token;
        localStorage.setItem('adhd_token', token);
        
        const refreshToken = response.data.refreshToken;
        if (refreshToken) {
          localStorage.setItem('adhd_refresh_token', refreshToken);
        }
        
        const decoded = decodeToken(token);
        if (decoded) {
          const extractedRole = extractRoleFromToken(decoded) as Role;
          localStorage.setItem('adhd_user', JSON.stringify({
            email,
            role: extractedRole
          }));

          set({
            token,
            role: extractedRole,
            isAuthenticated: true,
            isLoading: false
          });
        } else {
          throw new Error('Invalid token response structure.');
        }
      } else {
        throw new Error(response?.message || 'Authentication failed. Please verify credentials.');
      }
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('adhd_token');
    localStorage.removeItem('adhd_refresh_token');
    localStorage.removeItem('adhd_user');
    set({
      token: null,
      role: null,
      isAuthenticated: false,
      isLoading: false
    });
  }
}));
