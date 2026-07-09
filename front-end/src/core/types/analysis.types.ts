/** AI-processed analysis scores for a single session */
export interface AIAnalysisScores {
  attention: number;       // 0-100, higher is better
  impulsivity: number;     // 0-100, lower is better
  motorControl: number;    // 0-100, higher is better
}

/** Trend comparison vs previous sessions */
export interface AIAnalysisTrend {
  attentionChange: string | null;      // e.g. "+5%"
  impulsivityChange: string | null;    // e.g. "-8%"
  motorControlChange: string | null;   // e.g. "+3%"
}

/** Full AI analysis result for a session */
export interface AIAnalysis {
  sessionId: string;
  analysisDate: string;
  scores: AIAnalysisScores;
  trend: AIAnalysisTrend;
  summaryText: string | null;
  recommendations: string[] | null;
  modelUsed: string | null;
  isSuccessful: boolean;
  errorMessage: string | null;
}

/** AI analysis with game type context (from child analyses endpoint) */
export interface AIAnalysisWithGame extends Omit<AIAnalysis, 'recommendations' | 'modelUsed' | 'isSuccessful' | 'errorMessage'> {
  gameType: string;
  recommendations: string | null; // JSON string from the list endpoint
}
