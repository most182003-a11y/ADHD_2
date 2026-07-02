import React from "react";
import SectionCard from "@/components/SectionCard";
import StatCard from "@/components/StatCard";
import { Clock, Gamepad2, Award, Users, RefreshCw } from "lucide-react";
import { useAuthStore } from "@/core/auth/auth.store";
import { decodeToken, extractUserIdFromToken } from "@/core/auth/jwt.utils";
import { useChildren } from "@/hooks/useApiData";
import { useQueries } from "@tanstack/react-query";
import { childrenService } from "@/core/api/children.service";
import { queryKeys } from "@/core/constants/queryKeys";

export function ParentDashboardPage() {
  const token = useAuthStore((state) => state.token);
  
  // Extract parent ID from JWT token
  const parentId = React.useMemo(() => {
    if (!token) return "";
    const decoded = decodeToken(token);
    return decoded ? extractUserIdFromToken(decoded) : "";
  }, [token]);

  // Fetch children for this parent
  const { children, loading: loadingChildren, error: childrenError } = useChildren(parentId);

  // Fetch sessions for all children in parallel
  const sessionsQueries = useQueries({
    queries: (children || []).map((child) => ({
      queryKey: queryKeys.sessions.list(child.id),
      queryFn: () => childrenService.getSessions(child.id),
      enabled: !!child.id,
    })),
  });

  const loadingSessions = sessionsQueries.some((q) => q.isLoading);
  const sessionsError = sessionsQueries.find((q) => q.error)?.error;

  // Combine and sort all sessions by start time descending
  const allSessions = React.useMemo(() => {
    const combined = sessionsQueries.flatMap((q) => q.data || []);
    return combined.sort(
      (a, b) =>
        new Date(b.sessionInfo.startTime).getTime() -
        new Date(a.sessionInfo.startTime).getTime()
    );
  }, [sessionsQueries]);

  // Calculate statistics
  const stats = React.useMemo(() => {
    const totalPlaytimeMinutes = allSessions.reduce(
      (sum, s) => sum + (s.sessionInfo.durationMinutes || 0),
      0
    );
    const totalPlaytimeHours = Math.round((totalPlaytimeMinutes / 60) * 10) / 10;

    const totalGames = allSessions.length;

    const maxSuccess = allSessions.reduce(
      (max, s) => Math.max(max, s.summary?.success_rate || 0),
      0
    );

    return {
      playtime: totalPlaytimeHours > 0 ? `${totalPlaytimeHours} ساعة` : `${totalPlaytimeMinutes} دقيقة`,
      gamesCount: totalGames.toString(),
      bestScore: totalGames > 0 ? `${Math.round(maxSuccess)}%` : "0%",
    };
  }, [allSessions]);

  const isLoading = loadingChildren || loadingSessions;
  const hasError = childrenError || sessionsError;

  if (isLoading) {
    return (
      <div className="space-y-6 animate-pulse text-right" dir="rtl">
        <div>
          <div className="h-8 w-64 bg-muted rounded mb-2"></div>
          <div className="h-4 w-96 bg-muted rounded"></div>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-28 bg-card border rounded-xl p-6"></div>
          ))}
        </div>
        <div className="h-64 bg-card border rounded-xl p-6"></div>
      </div>
    );
  }

  if (hasError) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-center p-6 bg-card border rounded-xl space-y-4" dir="rtl">
        <div className="w-12 h-12 rounded-full bg-destructive/10 flex items-center justify-center">
          <RefreshCw className="w-6 h-6 text-destructive animate-spin" />
        </div>
        <h3 className="text-xl font-bold">عذراً، حدث خطأ أثناء تحميل البيانات</h3>
        <p className="text-muted-foreground max-w-md">يرجى التحقق من اتصالك بالشبكة أو المحاولة مرة أخرى لاحقاً.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in text-right" dir="rtl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2 font-display">لوحة تحكم ولي الأمر</h1>
        <p className="text-muted-foreground">أهلاً بك مجدداً! إليك ملخص تقدم أطفالك الأخير.</p>
      </div>

      {children.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-12 bg-card border rounded-xl text-center space-y-4">
          <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
            <Users className="w-8 h-8 text-primary" />
          </div>
          <h3 className="text-xl font-bold">لا يوجد أطفال مسجلين بعد</h3>
          <p className="text-muted-foreground max-w-sm">يرجى التواصل مع الطبيب المختص لربط حساب طفلك بحسابك وبدء متابعة تقدمه.</p>
        </div>
      ) : (
        <>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <StatCard
              title="إجمالي وقت اللعب"
              value={stats.playtime}
              subtitle="كافة الجلسات المسجلة"
              icon={<Clock className="h-4 w-4" />}
              variant="info"
            />
            <StatCard
              title="الألعاب الملعوبة"
              value={stats.gamesCount}
              subtitle="عدد الجلسات المكتملة"
              icon={<Gamepad2 className="h-4 w-4" />}
              variant="primary"
            />
            <StatCard
              title="أعلى نسبة نجاح"
              value={stats.bestScore}
              subtitle="أفضل أداء مسجل"
              icon={<Award className="h-4 w-4" />}
              variant="success"
            />
          </div>

          <SectionCard title="الجلسات الأخيرة" subtitle="نتائج آخر الألعاب التي لعبها أطفالك">
            {allSessions.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                لا توجد جلسات لعب مسجلة حتى الآن.
              </div>
            ) : (
              <div className="space-y-4">
                {allSessions.slice(0, 5).map((session, i) => {
                  const childName = children.find(c => c.id === session.sessionInfo.childId)?.name || "الطفل";
                  const formattedDate = new Date(session.sessionInfo.startTime).toLocaleDateString("ar-EG", {
                    weekday: "long",
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  });

                  return (
                    <div key={i} className="flex items-center justify-between p-4 border rounded-lg bg-card text-right">
                      <div className="text-left">
                        <div className="font-semibold text-lg text-primary">{Math.round(session.summary?.success_rate || 0)}%</div>
                        <div className="text-xs text-muted-foreground">{formattedDate}</div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <h4 className="font-semibold">{session.sessionInfo.game}</h4>
                          <p className="text-sm text-muted-foreground">الطفل: {childName}</p>
                        </div>
                        <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                          <Gamepad2 className="w-5 h-5 text-primary" />
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </SectionCard>
        </>
      )}
    </div>
  );
}

export default ParentDashboardPage;
