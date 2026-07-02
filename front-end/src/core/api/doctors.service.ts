import { apiClient } from './apiClient';
import type { Doctor } from '../types';
import { ApiResponse } from '../types/api.types';

export const doctorsService = {
  getDoctors: async (): Promise<Doctor[]> => {
    const res = await apiClient.get<ApiResponse<Doctor[]>>('doctors');
    if (!res.succeeded) throw new Error(res.message || 'Failed to fetch doctors');
    return res.data || [];
  }
};
