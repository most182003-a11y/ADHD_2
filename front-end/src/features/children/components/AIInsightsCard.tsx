import React from "react";
import { Brain, Star, TrendingUp, AlertCircle, Heart } from "lucide-react";
import SectionCard from "@/components/SectionCard";
import type { AIAnalysis } from "@/core/types/analysis.types";

interface AIInsightsCardProps {
  analysis: AIAnalysis | null;
  loading: boolean;
}

export default function AIInsightsCard({ analysis, loading }: AIInsightsCardProps) {
  if (loading) {
    return (
      <SectionCard title="تحليل الذكاء الاصطناعي والتوصيات" subtitle="جاري معالجة بيانات الجلسة بواسطة الوكيل الذكي...">
        <div className="space-y-4 animate-pulse">
          <div className="grid grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-20 bg-muted rounded-xl"></div>
            ))}
          </div>
          <div className="h-24 bg-muted rounded-xl"></div>
          <div className="h-20 bg-muted rounded-xl"></div>
        </div>
      </SectionCard>
    );
  }

  if (!analysis) {
    return (
      <SectionCard title="تحليل الذكاء الاصطناعي والتوصيات" subtitle="تحليل سلوكي وحركي متقدم">
        <div className="flex flex-col items-center justify-center p-8 text-center border border-dashed rounded-xl border-border bg-card">
          <Brain className="w-12 h-12 text-muted-foreground/50 mb-3" />
          <p className="text-sm font-semibold text-foreground">لم يتم إنشاء تحليل لهذه الجلسة بعد</p>
          <p className="text-xs text-muted-foreground mt-1 max-w-sm">
            يتم تشغيل وكيل الذكاء الاصطناعي تلقائياً فور حفظ ملخص الجلسة لإنتاج درجات الانتباه، الاندفاعية، والتحكم الحركي.
          </p>
        </div>
      </SectionCard>
    );
  }

  const { scores, trend, summaryText, recommendations } = analysis;

  const scoreItems = [
    {
      label: "درجة الانتباه والتركيز",
      value: scores.attention,
      change: trend.attentionChange,
      color: "from-blue-500 to-indigo-500",
      bg: "bg-blue-500/10",
      text: "text-blue-500",
      desc: "تقييم قدرة الطفل على تتبع المثيرات البصرية وتجنب المشتتات."
    },
    {
      label: "مؤشر التحكم في الاندفاعية",
      value: scores.impulsivity,
      change: trend.impulsivityChange,
      color: "from-amber-500 to-orange-500",
      bg: "bg-amber-500/10",
      text: "text-amber-500",
      desc: "تقييم التسرع والاستجابات الخاطئة قبل ظهور المثير المناسب."
    },
    {
      label: "تنسيق وثبات التحكم الحركي",
      value: scores.motorControl,
      change: trend.motorControlChange,
      color: "from-emerald-500 to-teal-500",
      bg: "bg-emerald-500/10",
      text: "text-emerald-500",
      desc: "تقييم ثبات الحركة وتفاعل الجسد أو المؤشر الحركي مع اللعبة."
    }
  ];

  const parseChange = (changeStr: string | null) => {
    if (!changeStr) return null;
    const value = parseFloat(changeStr.replace(/[^\d.-]/g, ''));
    if (isNaN(value)) return null;
    return {
      text: changeStr,
      isPositive: value >= 0
    };
  };

  return (
    <SectionCard
      title="التحليل الذكي للذكاء الاصطناعي والتوصيات"
      subtitle={`محلل بواسطة الوكيل الذكي (${analysis.modelUsed || "DeepSeek / HuggingFace"})`}
      className="border border-primary/20 shadow-lg relative overflow-hidden"
    >
      {/* Decorative top gradient glow */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-amber-500 to-emerald-500"></div>

      <div className="space-y-6">
        {/* Normalized Scores */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {scoreItems.map((item) => {
            const trendInfo = parseChange(item.change);
            return (
              <div
                key={item.label}
                className="flex flex-col justify-between p-4 rounded-xl bg-card/50 border border-border/80 hover:border-primary/20 transition-all duration-300 shadow-sm"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-muted-foreground">{item.label}</span>
                    {trendInfo && (
                      <span
                        className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                          trendInfo.isPositive
                            ? "bg-emerald-500/10 text-emerald-600"
                            : "bg-red-500/10 text-red-600"
                        }`}
                      >
                        {trendInfo.isPositive ? "↑" : "↓"} {trendInfo.text}
                      </span>
                    )}
                  </div>
                  <div className="mt-2 flex items-baseline gap-1">
                    <span className="text-3xl font-display font-bold text-foreground">
                      {Math.round(item.value)}
                    </span>
                    <span className="text-xs text-muted-foreground">/ 100</span>
                  </div>
                  {/* Custom animated progress bar */}
                  <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden mt-3">
                    <div
                      className={`h-full bg-gradient-to-r ${item.color} rounded-full transition-all duration-1000`}
                      style={{ width: `${Math.min(Math.max(item.value, 0), 100)}%` }}
                    ></div>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-3 leading-relaxed">
                  {item.desc}
                </p>
              </div>
            );
          })}
        </div>

        {/* Narrative Summary */}
        {summaryText && (
          <div className="p-4 rounded-xl border border-border bg-card/30 relative">
            <div className="flex items-center gap-2 mb-2">
              <Brain className="w-5 h-5 text-primary" />
              <h4 className="text-sm font-bold text-foreground">التقرير السلوكي والتحليلي للجلسة</h4>
            </div>
            <p className="text-sm text-foreground/90 leading-relaxed text-right whitespace-pre-wrap">
              {summaryText}
            </p>
          </div>
        )}

        {/* Actionable Recommendations */}
        {recommendations && recommendations.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Star className="w-5 h-5 text-amber-500 fill-amber-500" />
              <h4 className="text-sm font-bold text-foreground">توصيات مخصصة للآباء والمعالجين</h4>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {recommendations.map((rec, index) => (
                <div
                  key={index}
                  className="flex gap-3 p-3 rounded-lg border border-border/60 bg-muted/20 hover:bg-muted/40 transition-colors"
                >
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 text-primary flex items-center justify-center text-xs font-bold">
                    {index + 1}
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-foreground/90 leading-relaxed font-medium">
                      {rec}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </SectionCard>
  );
}
