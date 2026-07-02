import { useMemo } from "react";
import { Trophy, AlertTriangle } from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, Legend
} from "recharts";
import SectionCard from "@/components/SectionCard";
import StatCard from "@/components/StatCard";
import { useChildren, useSessions } from "@/hooks/useApiData";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { CustomTooltip } from "@/shared/components/data-display/CustomTooltip";

export function GameAnalyticsPage() {
  const { children, loading: loadingChildren } = useChildren();
  const { sessions: allSessions, loading: loadingSessions } = useSessions();

  const errorDist = useMemo(() => {
    const totFM = allSessions.reduce((s, sess) => s + (sess.summary.false_moves ?? 0), 0);
    const totFS = allSessions.reduce((s, sess) => s + (sess.summary.false_stops ?? 0), 0);
    return [
      { name: "حركات خاطئة", value: totFM },
      { name: "توقفات خاطئة", value: totFS },
    ];
  }, [allSessions]);

  const phaseData = useMemo(() => {
    const red = allSessions.reduce((s, sess) => s + (sess.summary.red_phase_errors ?? 0), 0);
    const green = allSessions.reduce((s, sess) => s + (sess.summary.green_phase_errors ?? 0), 0);
    return [
      { name: "أخطاء المرحلة الحمراء", value: red, fill: "#dc2626" },
      { name: "أخطاء المرحلة الخضراء", value: green, fill: "#16a34a" },
    ];
  }, [allSessions]);

  const sessionTrend = useMemo(() =>
    [...allSessions].reverse().slice(0, 20).map((s, i) => ({
      idx: `ج${i + 1}`,
      reaction: s.summary.avg_reaction_time * 1000,
      success: s.summary.success_rate,
    })), [allSessions]);

  const perChildData = useMemo(() =>
    children.map(child => {
      const sessions = allSessions.filter(s => s.sessionInfo.childId === child.id);
      if (!sessions.length) return null;
      const avgSuccess = sessions.reduce((s, sess) => s + sess.summary.success_rate, 0) / sessions.length;
      const avgReaction = sessions.reduce((s, sess) => s + sess.summary.avg_reaction_time, 0) / sessions.length;
      return { name: child.name.split(" ")[0], id: child.id, avgSuccess, avgReaction, sessions: sessions.length, initials: child.avatarInitials };
    }).filter(Boolean) as { name: string; id: string; avgSuccess: number; avgReaction: number; sessions: number; initials: string }[],
    [children, allSessions]);

  const bestPerformer = useMemo(() => [...perChildData].sort((a, b) => b.avgSuccess - a.avgSuccess)[0], [perChildData]);
  const worstPerformer = useMemo(() => [...perChildData].sort((a, b) => a.avgSuccess - b.avgSuccess)[0], [perChildData]);

  const totalFalseMoves = allSessions.reduce((s, sess) => s + (sess.summary.false_moves ?? 0), 0);
  const totalFalseStops = allSessions.reduce((s, sess) => s + (sess.summary.false_stops ?? 0), 0);
  const avgReaction = allSessions.length > 0 ? allSessions.reduce((s, sess) => s + sess.summary.avg_reaction_time, 0) / allSessions.length : 0;

  if (loadingChildren || loadingSessions) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-32 w-full rounded-xl" />)}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton className="h-[300px] w-full rounded-xl" />
          <Skeleton className="h-[300px] w-full rounded-xl" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 text-right" dir="rtl">
      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="إجمالي الحركات الخاطئة" value={totalFalseMoves} subtitle="لعبة التماثيل — كافة الجلسات" icon={<AlertTriangle size={18} />} variant="danger" />
        <StatCard title="إجمالي التوقفات الخاطئة" value={totalFalseStops} subtitle="لعبة التماثيل — كافة الجلسات" icon={<AlertTriangle size={18} />} variant="amber" />
        <StatCard title="متوسط زمن الاستجابة" value={`${(avgReaction * 1000).toFixed(0)} مل ث`} subtitle="متوسط سرعة الاستجابة" icon={<Trophy size={18} />} variant="info" />
        <StatCard title="إجمالي الجلسات" value={allSessions.length} subtitle="لعبة التماثيل" icon={<Trophy size={18} />} variant="success" />
      </div>

      {/* Error Distribution + Phase Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SectionCard title="توزيع أنواع الأخطاء" subtitle="الحركات الخاطئة مقابل التوقفات الخاطئة (جميع الجلسات)">
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={errorDist} cx="50%" cy="50%" outerRadius={80} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`} labelLine={false}>
                <Cell fill="#dc2626" />
                <Cell fill="#d97706" />
              </Pie>
              <Legend iconType="circle" iconSize={8} formatter={(v) => <span className="text-xs text-foreground">{v}</span>} />
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </SectionCard>

        <SectionCard title="تحليل أخطاء المراحل" subtitle="المرحلة الحمراء مقابل المرحلة الخضراء">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={phaseData} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} className="stroke-border" />
              <XAxis type="number" tick={{ fontSize: 11 }} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={120} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="value" name="الأخطاء" radius={[0, 6, 6, 0]}>
                {phaseData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div className="mt-3 flex gap-6 text-xs text-right">
            <div className="flex flex-col gap-0.5">
              <span className="text-muted-foreground font-semibold">المرحلة الحمراء (التجميد)</span>
              <span className="font-bold text-danger">{phaseData[0].value} خطأ</span>
            </div>
            <div className="flex flex-col gap-0.5">
              <span className="text-muted-foreground font-semibold">المرحلة الخضراء (الحركة)</span>
              <span className="font-bold text-success">{phaseData[1].value} خطأ</span>
            </div>
          </div>
        </SectionCard>
      </div>

      {/* Reaction Time Trend */}
      <SectionCard title="منحنى زمن الاستجابة" subtitle="متوسط زمن الاستجابة عبر الجلسات (أول ٢٠ جلسة)">
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={sessionTrend} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
            <XAxis dataKey="idx" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} unit="مل ث" />
            <Tooltip content={<CustomTooltip />} />
            <Line type="monotone" dataKey="reaction" name="زمن الاستجابة (ملي ثانية)" stroke="hsl(205,80%,50%)" strokeWidth={2.5} dot={{ r: 3, fill: "hsl(205,80%,50%)" }} />
          </LineChart>
        </ResponsiveContainer>
      </SectionCard>

      {/* Per-Child Performance */}
      <SectionCard title="أداء الأطفال" subtitle="مقارنة متوسط معدلات النجاح للأطفال">
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={perChildData} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
            <XAxis dataKey="name" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} domain={[50, 100]} unit="%" />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="avgSuccess" name="متوسط النجاح %" fill="hsl(193,72%,28%)" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </SectionCard>

      {/* Best / Worst */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {[
          { label: "🏆 أفضل أداء", child: bestPerformer, cls: "border-success/40 bg-success-bg" },
          { label: "⚠️ الأكثر احتياجاً للمتابعة", child: worstPerformer, cls: "border-danger/40 bg-danger-bg" },
        ].map(({ label, child, cls }) => child && (
          <div key={label} className={cn("rounded-xl border p-5 flex items-center justify-end gap-4", cls)}>
            <div className="text-right">
              <p className="text-xs font-semibold text-muted-foreground mb-1">{label}</p>
              <p className="font-bold text-foreground">{children.find(c => c.id === child.id)?.name}</p>
              <p className="text-sm text-muted-foreground">متوسط نجاح {child.avgSuccess.toFixed(1)}% · تم إتمام {child.sessions} جلسة</p>
            </div>
            <div className="w-12 h-12 rounded-full gradient-primary flex items-center justify-center flex-shrink-0">
              <span className="text-base font-bold text-primary-foreground">{child.initials}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default GameAnalyticsPage;
