import { Session, Child, SessionSummary } from "@/core/types";
import { targets } from "@/core/constants/targets";

export type { Session, Child, SessionSummary };
export { targets };

export const generateRecommendations = (sessions: Session[]): string[] => {
  if (sessions.length === 0) return ["No session data available to generate recommendations."];
  
  // Extract last session summary
  // We assume that the sessions array might have items with either backend property naming (camelCase) or snake_case.
  // Let's handle both gracefully for robust clinical recommendation parsing.
  const lastSession = sessions[sessions.length - 1];
  if (!lastSession || !lastSession.summary) {
    return ["No session data available to generate recommendations."];
  }
  
  const summary = lastSession.summary;
  
  // Safely extract properties handling snake_case (legacy data-utils compatibility)
  const motor_control_score = summary.motor_control_score ?? (summary as any).motorControlScore ?? 0;
  const impulsivity_index = summary.impulsivity_index ?? (summary as any).impulsivityIndex ?? 0;
  const distraction_score = summary.distraction_score ?? (summary as any).distractionScore ?? 0;
  const avg_reaction_time = summary.avg_reaction_time ?? (summary as any).avgReactionTime ?? 0;
  const success_rate = summary.success_rate ?? (summary as any).successRate ?? 0;
  const false_moves = summary.false_moves ?? (summary as any).falseMoves ?? 0;

  const recs: string[] = [];
  if (motor_control_score < 70) recs.push("Motor control below target — intensify balance & stillness training exercises");
  if (impulsivity_index > 18) recs.push("High impulsivity index — increase sudden-stop exercises and delay-of-gratification tasks");
  if (distraction_score > 20) recs.push("Elevated distraction score — reduce environmental stimuli during sessions");
  if (avg_reaction_time > 0.55) recs.push("Slow reaction time — introduce rhythm-based response activities");
  if (false_moves > 4) recs.push("Excessive false moves in red phase — reinforce inhibition cues with visual feedback");
  if (success_rate > 85) recs.push("Strong success rate — consider advancing to next difficulty level");
  if (recs.length === 0) recs.push("Performance within target range — maintain current training protocol");
  
  return recs;
};
