export interface SessionSummary {
  total_trials: number;
  success_rate: number;
  impulsivity_index: number;
  motor_control_score: number;
  distraction_score: number;
  avg_reaction_time: number;
  max_consecutive_success: number;
  false_moves?: number;
  false_stops?: number;
  red_phase_errors?: number;
  green_phase_errors?: number;
}

export interface Session {
  sessionInfo: {
    childId: string;
    sessionId: string;
    startTime: string;
    durationMinutes: number;
    therapist: string;
    game: string;
  };
  summary: SessionSummary;
}
