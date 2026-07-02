export const severityMapArabic = (sev: string, context: 'masculine' | 'feminine' = 'feminine'): string => {
  switch (sev?.toLowerCase()) {
    case 'mild':
      return context === 'feminine' ? 'بسيطة' : 'بسيط';
    case 'moderate':
      return context === 'feminine' ? 'متوسطة' : 'متوسط';
    case 'severe':
      return context === 'feminine' ? 'شديدة' : 'شديد';
    default:
      return sev || 'غير محدد';
  }
};

export const statusMapArabic = (status: string): string => {
  switch (status?.toLowerCase()) {
    case 'improving': return 'يتحسن';
    case 'stable': return 'مستقر';
    case 'needs_intervention': return 'بحاجة لتدخل';
    default: return status || 'غير محدد';
  }
};
