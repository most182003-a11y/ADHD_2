export interface MetricDetail {
  ar: string;
  en: string;
  desc: string;
  color: string;
}

export const METRICS_MAP: Record<string, MetricDetail> = {
  MotorControlScore: {
    ar: "مقياس التحكم الحركي",
    en: "Motor Control Score",
    desc: "يقيس مدى قدرة الطفل على تثبيت جسده والتحكم في حركاته البدنية عند إشارة التوقف.",
    color: "bg-emerald-50 text-emerald-700 border-emerald-200"
  },
  ImpulsivityIndex: {
    ar: "مؤشر الاندفاعية",
    en: "Impulsivity Index",
    desc: "يقيس ردود الفعل الاستباقية أو التسرع في اتخاذ القرارات قبل ظهور الإشارة الصحيحة.",
    color: "bg-amber-50 text-amber-700 border-amber-200"
  },
  FalseMoves: {
    ar: "الحركات الخاطئة",
    en: "False Moves",
    desc: "عدد المرات التي تحرك فيها الطفل أثناء مرحلة السكون المطلوبة.",
    color: "bg-rose-50 text-rose-700 border-rose-200"
  },
  AvgReactionTime: {
    ar: "متوسط زمن الاستجابة",
    en: "Average Reaction Time",
    desc: "يقيس سرعة المعالجة العصبية وزمن الاستجابة للمؤثرات البصرية.",
    color: "bg-blue-50 text-blue-700 border-blue-200"
  },
  DistractionScore: {
    ar: "معدل التشتت",
    en: "Distraction Score",
    desc: "يقيس مدى تأثير المشتتات البصرية أو السمعية الجانبية على أداء واستجابة الطفل.",
    color: "bg-purple-50 text-purple-700 border-purple-200"
  },
  SuccessRate: {
    ar: "نسبة النجاح الإجمالية",
    en: "Success Rate",
    desc: "النسبة المئوية للاستجابات الصحيحة مقارنة بالعدد الإجمالي للمحاولات في الجلسة.",
    color: "bg-indigo-50 text-indigo-700 border-indigo-200"
  },
  FalseStops: {
    ar: "التوقفات الخاطئة",
    en: "False Stops",
    desc: "عدد التوقفات غير المبررة أو التردد عند ظهور إشارات الاستجابة النشطة.",
    color: "bg-orange-50 text-orange-700 border-orange-200"
  },
  MaxConsecutiveSuccess: {
    ar: "أقصى نجاح متتالي",
    en: "Max Consecutive Success",
    desc: "أعلى سلسلة من الاستجابات الصحيحة المتتالية، مما يعكس مستوى الانتباه المستدام.",
    color: "bg-teal-50 text-teal-700 border-teal-200"
  },
  TotalTrials: {
    ar: "إجمالي المحاولات",
    en: "Total Trials",
    desc: "العدد الكلي للمحاولات التي خاضها الطفل خلال فترة تشغيل اللعبة.",
    color: "bg-slate-50 text-slate-700 border-slate-200"
  }
} as const;

export const getMetricDetails = (metricKey: string): MetricDetail => {
  return METRICS_MAP[metricKey] || {
    ar: metricKey,
    en: metricKey,
    desc: "مقياس خاص لتحليل السلوك ومعدل التركيز.",
    color: "bg-slate-50 text-slate-700 border-slate-200"
  };
};
