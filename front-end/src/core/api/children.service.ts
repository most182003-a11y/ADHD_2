import { apiClient } from './apiClient';
import type { Child, Session } from '../types';
import { ApiResponse } from '../types/api.types';
import { mapChildFromBackend, mapSessionFromBackend } from '../utils/mappers';

export const childrenService = {
  getChildren: async (parentId?: string): Promise<Child[]> => {
    const res = await apiClient.get<ApiResponse<any[]>>(
      'children',
      parentId ? { params: { parentId } } : undefined
    );
    if (!res.succeeded) throw new Error(res.message || 'Failed to fetch children');
    return (res.data || []).map(mapChildFromBackend);
  },

  getSessions: async (childId?: string): Promise<Session[]> => {
    const res = await apiClient.get<ApiResponse<any[]>>(
      'sessions',
      childId ? { params: { childId } } : undefined
    );
    if (!res.succeeded) throw new Error(res.message || 'Failed to fetch sessions');
    return (res.data || []).map(mapSessionFromBackend);
  }
};
