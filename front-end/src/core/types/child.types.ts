export interface Child {
  id: string;
  name: string;
  age: number;
  gender: "male" | "female";
  diagnosisSeverity: "mild" | "moderate" | "severe";
  registeredDate: string;
  therapist: string;
  status: "improving" | "stable" | "needs_intervention";
  avatarInitials: string;
  doctorId?: string;
  parentId?: string;
}
