import { apiClient } from './apiClient';
import type { Game } from '../types';
import { ApiResponse } from '../types/api.types';

export const gamesService = {
  getGames: async (): Promise<Game[]> => {
    const res = await apiClient.get<ApiResponse<Game[]>>('games');
    if (!res.succeeded) throw new Error(res.message || 'Failed to fetch games');
    return res.data || [];
  }
};
