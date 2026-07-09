import { apiClient } from './apiClient';
import type { AIAnalysis, AIAnalysisWithGame } from '../types/analysis.types';

interface ApiResponse<T> {
  succeeded: boolean;
  data: T;
  message?: string;
}

/**
 * Fetch the AI analysis result for a specific session.
 */
export async function getSessionAnalysis(sessionId: string): Promise<AIAnalysis | null> {
  try {
    const res = await apiClient.get<ApiResponse<AIAnalysis>>(`Sessions/${sessionId}/analysis`);
    return res.succeeded ? res.data : null;
  } catch {
    return null;
  }
}

/**
 * Fetch all AI analyses for a child (across all their sessions).
 */
export async function getChildAnalyses(childId: string): Promise<AIAnalysisWithGame[]> {
  try {
    const res = await apiClient.get<ApiResponse<AIAnalysisWithGame[]>>(`Sessions/child/${childId}/analyses`);
    return res.succeeded ? res.data : [];
  } catch {
    return [];
  }
}
