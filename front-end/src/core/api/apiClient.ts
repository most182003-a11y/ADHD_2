import { decodeToken } from '../auth/jwt.utils';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5131/api';

export interface RequestOptions extends RequestInit {
  params?: Record<string, string>;
}

let refreshPromise: Promise<string> | null = null;

async function performTokenRefresh(accessToken: string, refreshToken: string): Promise<string> {
  if (refreshPromise) {
    return refreshPromise;
  }

  refreshPromise = (async () => {
    try {
      const refreshRes = await fetch(`${API_BASE_URL}/Account/refresh-token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ accessToken, refreshToken }),
      });
      
      if (refreshRes.ok) {
        const refreshData = await refreshRes.json();
        if (refreshData.succeeded && refreshData.data?.token) {
          const newToken = refreshData.data.token;
          const newRefreshToken = refreshData.data.refreshToken;
          
          localStorage.setItem('adhd_token', newToken);
          if (newRefreshToken) {
            localStorage.setItem('adhd_refresh_token', newRefreshToken);
          }
          
          refreshPromise = null;
          return newToken;
        }
      }
      throw new Error('Failed to refresh token');
    } catch (err) {
      refreshPromise = null;
      localStorage.removeItem('adhd_token');
      localStorage.removeItem('adhd_refresh_token');
      localStorage.removeItem('adhd_user');
      window.dispatchEvent(new Event('auth_session_expired'));
      throw new Error('Session expired. Please log in again.');
    }
  })();

  return refreshPromise;
}

function handleSessionExpired() {
  localStorage.removeItem('adhd_token');
  localStorage.removeItem('adhd_refresh_token');
  localStorage.removeItem('adhd_user');
  window.dispatchEvent(new Event('auth_session_expired'));
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { params, headers, ...customConfig } = options;
  
  // Construct Query Parameters if any
  let url = `${API_BASE_URL}/${endpoint.replace(/^\//, '')}`;
  if (params) {
    const searchParams = new URLSearchParams(params);
    url += `?${searchParams.toString()}`;
  }

  // Retrieve Token from Storage
  let token = localStorage.getItem('adhd_token');
  const refreshToken = localStorage.getItem('adhd_refresh_token');

  // Proactive Expiry Check: Before each request, check exp
  if (token) {
    const decoded = decodeToken(token);
    if (decoded && decoded.exp && decoded.exp * 1000 <= Date.now()) {
      if (refreshToken) {
        try {
          // Attempt token refresh proactively
          token = await performTokenRefresh(token, refreshToken);
        } catch (err) {
          throw new Error('Session expired. Please log in again.');
        }
      } else {
        handleSessionExpired();
        throw new Error('Session expired. Please log in again.');
      }
    }
  }

  // Merge default and custom headers
  const requestHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((headers as Record<string, string>) || {}),
  };

  if (token) {
    requestHeaders['Authorization'] = `Bearer ${token}`;
  }

  const config: RequestInit = {
    ...customConfig,
    headers: requestHeaders,
  };

  const response = await fetch(url, config);

  // Global 401 Interceptor: Attempt Refresh Token as fallback
  if (response.status === 401) {
    const activeRefreshToken = localStorage.getItem('adhd_refresh_token');
    const activeAccessToken = localStorage.getItem('adhd_token');
    
    if (activeRefreshToken && activeAccessToken) {
      try {
        const newToken = await performTokenRefresh(activeAccessToken, activeRefreshToken);
        
        // Retry current request
        const retryHeaders: Record<string, string> = {
          ...requestHeaders,
          'Authorization': `Bearer ${newToken}`,
        };
        return request<T>(endpoint, { ...options, headers: retryHeaders });
      } catch (err) {
        throw new Error('Session expired. Please log in again.');
      }
    } else {
      handleSessionExpired();
      throw new Error('Session expired. Please log in again.');
    }
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.Message || `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export const apiClient = {
  request,

  get<T>(endpoint: string, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<T> {
    return request<T>(endpoint, { ...options, method: 'GET' });
  },

  post<T>(endpoint: string, body: any, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<T> {
    return request<T>(endpoint, { 
      ...options, 
      method: 'POST', 
      body: JSON.stringify(body) 
    });
  },

  put<T>(endpoint: string, body: any, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<T> {
    return request<T>(endpoint, { 
      ...options, 
      method: 'PUT', 
      body: JSON.stringify(body) 
    });
  },

  delete<T>(endpoint: string, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<T> {
    return request<T>(endpoint, { ...options, method: 'DELETE' });
  }
};
