export const CLINICAL_TARGETS = {
  impulsivity_index: 10,
  motor_control_score: 85,
  distraction_score: 10,
  avg_reaction_time: 0.35,
  success_rate: 90,
} as const;

// Backward-compatible export
export const targets = CLINICAL_TARGETS;
