import type { Child, Session } from '../types';

export const mapChildFromBackend = (c: Record<string, any>): Child => {
  const genderMap: Record<number, "male" | "female"> = {
    0: "male",
    1: "female"
  };
  const severityMap: Record<number, "mild" | "moderate" | "severe"> = {
    0: "mild",
    1: "moderate",
    2: "severe"
  };
  const statusMap: Record<number, "improving" | "stable" | "needs_intervention"> = {
    0: "improving",
    1: "stable",
    2: "needs_intervention"
  };

  return {
    id: c.id,
    name: c.name,
    age: c.age,
    gender: genderMap[c.gender] || "male",
    diagnosisSeverity: severityMap[c.diagnosisSeverity] || "moderate",
    registeredDate: c.registeredDate ? c.registeredDate.split("T")[0] : new Date().toISOString().split("T")[0],
    therapist: c.doctor ? `د. ${c.doctor.userName}` : "غير معين",
    status: statusMap[c.status] || "stable",
    avatarInitials: c.avatarInitials || "CH",
    doctorId: c.doctorId || undefined,
    parentId: c.parentId || undefined
  };
};

export const mapSessionFromBackend = (s: Record<string, any>): Session => {
  const impulsivity = (s.impulsivityIndex !== undefined && s.impulsivityIndex !== null) ? s.impulsivityIndex * 100 : 0;
  const motorControl = (s.motorControlScore !== undefined && s.motorControlScore !== null) ? s.motorControlScore * 100 : 0;
  const distraction = (s.distractionScore !== undefined && s.distractionScore !== null) ? s.distractionScore * 100 : 0;
  const reactionTime = (s.avgReactionTime !== undefined && s.avgReactionTime !== null) ? s.avgReactionTime / 1000 : 0;

  return {
    sessionInfo: {
      childId: s.childId,
      sessionId: s.id,
      startTime: s.startTime,
      durationMinutes: s.durationMinutes,
      therapist: s.doctor ? `د. ${s.doctor.userName}` : "غير معين",
      game: s.gameId || s.gameName || "Simon Game"
    },
    summary: {
      total_trials: s.totalTrials || 0,
      success_rate: s.successRate || 0,
      impulsivity_index: impulsivity,
      motor_control_score: motorControl,
      distraction_score: distraction,
      avg_reaction_time: reactionTime,
      max_consecutive_success: s.maxConsecutiveSuccess || 0,
      false_moves: s.falseMoves || 0,
      false_stops: s.falseStops || 0,
      red_phase_errors: s.falseMoves || 0,
      green_phase_errors: s.falseStops || 0
    }
  };
};
