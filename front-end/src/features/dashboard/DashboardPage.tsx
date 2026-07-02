import { useMemo } from "react";
import { Users, Activity, TrendingUp, Calendar } from "lucide-react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from "recharts";
import StatCard from "@/components/StatCard";
import SectionCard from "@/components/SectionCard";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { useChildren, useSessions } from "@/hooks/useApiData";
import { Skeleton } from "@/components/ui/skeleton";
import { CustomTooltip } from "@/shared/components/data-display/CustomTooltip";

const STATUS_COLORS = {
  improving: { label: "يتحسن", color: "#16a34a", bg: "status-success" },
  stable: { label: "مستقر", color: "#d97706", bg: "status-warning" },
  needs_intervention: { label: "بحاجة لتدخل", color: "#dc2626", bg: "status-danger" },
};

const PIE_COLORS = ["#16a34a", "#d97706", "#dc2626"];

export function DashboardPage() {
  const { children, loading: loadingChildren } = useChildren();
  const { sessions: allSessions, loading: loadingSessions } = useSessions();

  const recentSessions = useMemo(() => allSessions.slice(0, 5), [allSessions]);

  const totalSessions = allSessions.length;
  const avgImprovement = totalSessions > 0 ? Math.round(
    allSessions.reduce((sum, s) => sum + s.summary.success_rate, 0) / totalSessions
  ) : 0;

  const now = useMemo(() => {
    if (allSessions.length === 0) return new Date();
    const maxTime = Math.max(...allSessions.map(s => new Date(s.sessionInfo.startTime).getTime()));
    return new Date(maxTime);
  }, [allSessions]);

  const sessionsThisWeek = useMemo(() => {
    const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    return allSessions.filter(s => new Date(s.sessionInfo.startTime) > oneWeekAgo).length;
  }, [allSessions, now]);

  const activeChildrenThisWeek = useMemo(() => {
    const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    const recent = allSessions.filter(s => new Date(s.sessionInfo.startTime) > oneWeekAgo);
    const uniqueChildIds = new Set(recent.map(s => s.sessionInfo.childId));
    return uniqueChildIds.size;
  }, [allSessions, now]);

  const dynamicWeeklyProgress = useMemo(() => {
    const weeks: Record<string, { successSum: number; count: number; sessionCount: number }> = {};

    for (let i = 5; i >= 0; i--) {
      const weekLabel = `الأسبوع ${6 - i}`;
      weeks[weekLabel] = { successSum: 0, count: 0, sessionCount: 0 };
    }

    allSessions.forEach(s => {
      const sDate = new Date(s.sessionInfo.startTime);
      const diffDays = Math.floor((now.getTime() - sDate.getTime()) / (24 * 60 * 60 * 1000));
      const weekIdx = Math.floor(diffDays / 7);

      if (weekIdx >= 0 && weekIdx < 6) {
        const weekLabel = `الأسبوع ${6 - weekIdx}`;
        if (weeks[weekLabel]) {
          weeks[weekLabel].successSum += s.summary.success_rate;
          weeks[weekLabel].count++;
          weeks[weekLabel].sessionCount++;
        }
      }
    });

    return Object.entries(weeks).map(([week, data]) => ({
      week,
      avg_improvement: data.count > 0 ? Math.round(data.successSum / data.count) : 0,
      sessions: data.sessionCount
    }));
  }, [allSessions, now]);

  const statusDist = useMemo(() => {
    const counts = { improving: 0, stable: 0, needs_intervention: 0 };
    children.forEach(c => {
      if (counts[c.status] !== undefined) {
        counts[c.status]++;
      }
    });
    return [
      { name: "يتحسن", value: counts.improving },
      { name: "مستقر", value: counts.stable },
      { name: "بحاجة لتدخل", value: counts.needs_intervention },
    ];
  }, [children]);

  if (loadingChildren || loadingSessions) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-32 w-full rounded-xl" />)}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Skeleton className="lg:col-span-2 h-[300px] w-full rounded-xl" />
          <Skeleton className="h-[300px] w-full rounded-xl" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="الأطفال المسجلين"
          value={children.length}
          subtitle="المرضى النشطين"
          icon={<Users size={20} />}
          variant="primary"
        />
        <StatCard
          title="إجمالي الجلسات"
          value={totalSessions}
          subtitle="كافة الأوقات"
          icon={<Activity size={20} />}
          variant="amber"
        />
        <StatCard
          title="متوسط نسبة النجاح"
          value={`${avgImprovement}%`}
          subtitle="عبر جميع الجلسات"
          icon={<TrendingUp size={20} />}
          variant="success"
        />
        <StatCard
          title="جلسات هذا الأسبوع"
          value={sessionsThisWeek}
          subtitle={`نشاط ${activeChildrenThisWeek} من الأطفال`}
          icon={<Calendar size={20} />}
          variant="info"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Line Chart */}
        <SectionCard
          title="اتجاه التحسن الأسبوعي"
          subtitle="متوسط نسبة النجاح وعدد الجلسات خلال آخر ٦ أسابيع"
          className="lg:col-span-2"
        >
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={dynamicWeeklyProgress} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="week" tick={{ fontSize: 11 }} className="fill-muted-foreground" />
              <YAxis tick={{ fontSize: 11 }} domain={[0, 100]} className="fill-muted-foreground" />
              <Tooltip content={
                <CustomTooltip 
                  valueFormatter={(v) => typeof v === 'number' ? v.toFixed(1) : v}
                />
              } />
              <Line
                type="monotone"
                dataKey="avg_improvement"
                name="نسبة النجاح %"
                stroke="hsl(193,72%,28%)"
                strokeWidth={2.5}
                dot={{ r: 3, fill: "hsl(193,72%,28%)" }}
                activeDot={{ r: 5 }}
              />
              <Line
                type="monotone"
                dataKey="sessions"
                name="عدد الجلسات"
                stroke="hsl(38,93%,52%)"
                strokeWidth={2}
                dot={{ r: 3, fill: "hsl(38,93%,52%)" }}
                strokeDasharray="5 3"
              />
            </LineChart>
          </ResponsiveContainer>
        </SectionCard>

        {/* Pie Chart */}
        <SectionCard title="توزيع حالة المرضى" subtitle="تحليل إحصائي وتوزيع لحالات الأطفال الحالية">
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie
                data={statusDist}
                cx="50%"
                cy="50%"
                innerRadius={48}
                outerRadius={72}
                paddingAngle={3}
                dataKey="value"
              >
                {statusDist.map((_, i) => (
                  <Cell key={i} fill={PIE_COLORS[i]} />
                ))}
              </Pie>
              <Legend
                iconType="circle"
                iconSize={8}
                formatter={(v) => <span className="text-xs text-foreground">{v}</span>}
              />
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex flex-col gap-1.5 mt-1">
            {statusDist.map((s, i) => (
              <div key={s.name} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full" style={{ background: PIE_COLORS[i] }} />
                  <span className="text-muted-foreground">{s.name}</span>
                </div>
                <span className="font-semibold text-foreground">{s.value}</span>
              </div>
            ))}
          </div>
        </SectionCard>
      </div>

      {/* Recent Sessions */}
      <SectionCard title="الجلسات الأخيرة" subtitle="آخر ٥ جلسات تدريبية تم تسجيلها" noPadding>
        <div className="divide-y divide-border">
          {recentSessions.map((session) => {
            const child = children.find(c => c.id === session.sessionInfo.childId);
            const status = child ? STATUS_COLORS[child.status] : STATUS_COLORS.stable;

            const date = new Date(session.sessionInfo.startTime);
            return (
              <div key={session.sessionInfo.sessionId} className="flex items-center gap-4 px-5 py-3.5 hover:bg-muted/40 transition-colors">
                <div className="w-9 h-9 rounded-full gradient-primary flex items-center justify-center flex-shrink-0">
                  <span className="text-xs font-bold text-primary-foreground">{child?.avatarInitials || "?"}</span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-foreground truncate">{child?.name || session.sessionInfo.childId}</p>
                  <p className="text-xs text-muted-foreground">
                    {date.toLocaleDateString('ar-EG')} · {session.sessionInfo.durationMinutes} دقيقة · {session.summary.total_trials} محاولة
                  </p>
                </div>
                <div className="text-right flex-shrink-0">
                  <p className="text-sm font-bold text-foreground">{session.summary.success_rate.toFixed(1)}%</p>
                  <p className="text-xs text-muted-foreground">معدل النجاح</p>
                </div>
                <Badge className={cn("text-xs hidden sm:flex", status.bg)}>
                  {status.label}
                </Badge>
              </div>
            );
          })}
        </div>
      </SectionCard>

      {/* Children Grid */}
      <SectionCard title="جميع الأطفال المرضى" subtitle={`إجمالي الأطفال المسجلين: ${children.length}`}>
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
          {children.map(child => {
            const st = STATUS_COLORS[child.status] || STATUS_COLORS.stable;
            const childSessions = allSessions.filter(s => s.sessionInfo.childId === child.id);

            const lastSession = childSessions[childSessions.length - 1];
            return (
              <div key={child.id} className="flex items-center gap-3 p-3 rounded-lg border border-border hover:border-primary/30 hover:bg-muted/30 transition-all">
                <div className="w-10 h-10 rounded-full gradient-primary flex items-center justify-center flex-shrink-0">
                  <span className="text-sm font-bold text-primary-foreground">{child.avatarInitials}</span>
                </div>
                <div className="flex-1 min-w-0 text-right">
                  <p className="text-sm font-semibold text-foreground truncate">{child.name}</p>
                  <p className="text-xs text-muted-foreground">العمر: {child.age} سنوات · {childSessions.length} جلسة</p>
                </div>
                <div className="flex flex-col items-end gap-1">
                  <Badge className={cn("text-xs", st.bg)}>{st.label}</Badge>
                  {lastSession && (
                    <span className="text-xs font-semibold text-foreground">{lastSession.summary.success_rate.toFixed(0)}%</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </SectionCard>
    </div>
  );
}

export default DashboardPage;
