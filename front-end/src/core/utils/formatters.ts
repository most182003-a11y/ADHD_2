export const formatDoctorName = (name: string): string => {
  if (!name) return "";
  const cleanName = name.replace(/_/g, " ").trim();
  if (/^د[\.\s_]+/i.test(cleanName)) {
    return cleanName.replace(/^د[\.\s_]+/i, "د. ").trim();
  }
  return `د. ${cleanName}`;
};
