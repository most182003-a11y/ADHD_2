import { apiClient } from './apiClient';
import type { Parent } from '../types';
import { ApiResponse } from '../types/api.types';

export const parentsService = {
  getParents: async (): Promise<Parent[]> => {
    const res = await apiClient.get<ApiResponse<Parent[]>>('parents');
    if (!res.succeeded) throw new Error(res.message || 'Failed to fetch parents');
    return res.data || [];
  }
};
