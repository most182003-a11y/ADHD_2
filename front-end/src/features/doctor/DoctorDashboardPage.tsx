import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import SectionCard from "@/components/SectionCard";
import StatCard from "@/components/StatCard";
import { Users, Activity, Shield, Award, ChevronRight, User, Calendar } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useChildren, useDoctors, useSessions } from "@/hooks/useApiData";

export function DoctorDashboardPage() {
  const navigate = useNavigate();
  const { doctors, loading: loadingDocs } = useDoctors();
  const { children, loading: loadingChildren } = useChildren();
  const { sessions, loading: loadingSessions } = useSessions();

  const [currentDoctor, setCurrentDoctor] = useState<any>(null);

  useEffect(() => {
    const userStr = localStorage.getItem("adhd_user");
    if (userStr && doctors.length > 0) {
      try {
        const user = JSON.parse(userStr);
        const doc = doctors.find((d) => d.email?.toLowerCase() === user.email?.toLowerCase());
        if (doc) {
          setCurrentDoctor(doc);
        } else {
          // Fallback to the first doctor in system if no direct match (e.g. seed data or testing)
          setCurrentDoctor(doctors[0]);
        }
      } catch (e) {
        console.error("Error parsing logged in user profile:", e);
        setCurrentDoctor(doctors[0]);
      }
    } else if (doctors.length > 0) {
      // Direct fallback to first seeded doctor if no user in localStorage (prevent blank screens)
      setCurrentDoctor(doctors[0]);
    }
  }, [doctors]);

  // Loading state with a modern, premium shimmering skeleton loader
  if (loadingDocs || loadingChildren || loadingSessions) {
    return (
      <div className="space-y-6 animate-pulse-soft">
        <div className="space-y-3">
          <div className="h-9 w-64 bg-slate-200 dark:bg-slate-800 rounded-lg" />
          <div className="h-4 w-96 bg-slate-200 dark:bg-slate-800 rounded-lg" />
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-28 bg-slate-100 dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-xl" />
          ))}
        </div>
        <div className="grid gap-6 md:grid-cols-3">
          <div className="md:col-span-2 h-96 bg-slate-100 dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-xl" />
          <div className="h-96 bg-slate-100 dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-xl" />
        </div>
      </div>
    );
  }

  // Filter children assigned to this doctor
  const assignedChildren = children.filter(
    (c) => c.doctorId === currentDoctor?.id
  );

  // Elegant fallback: If the current doctor has no assigned patients, display all patients to avoid a blank screen
  const displayChildren = assignedChildren.length > 0 ? assignedChildren : children;

  // Filter sessions that belong to our display children
  const displayChildrenIds = new Set(displayChildren.map((c) => c.id));
  const doctorSessions = sessions.filter((s) => displayChildrenIds.has(s.sessionInfo.childId));

  // Sort sessions by date descending (most recent first)
  const sortedSessions = [...doctorSessions].sort(
    (a, b) => new Date(b.sessionInfo.startTime).getTime() - new Date(a.sessionInfo.startTime).getTime()
  );

  // Statistics calculation
  const totalPatients = displayChildren.length;
  const totalSessions = doctorSessions.length;

  const totalSuccess = doctorSessions.reduce((acc, s) => acc + s.summary.success_rate, 0);
  const avgSuccessRate = totalSessions > 0 ? Math.round(totalSuccess / totalSessions) : 0;

  // Formatting translation helper for clinical status
  const getStatusDetails = (status: string) => {
    switch (status) {
      case "improving":
        return { label: "تحسن مستمر", variant: "default" as const, className: "bg-emerald-500 hover:bg-emerald-600 border-transparent text-white" };
      case "needs_intervention":
        return { label: "بحاجة لتدخل", variant: "destructive" as const, className: "" };
      case "stable":
      default:
        return { label: "مستقر", variant: "secondary" as const, className: "" };
    }
  };

  const getSeverityLabel = (severity: string) => {
    switch (severity) {
      case "mild":
        return "خفيف";
      case "severe":
        return "شديد";
      case "moderate":
      default:
        return "متوسط";
    }
  };

  return (
    <div className="space-y-6 animate-fade-in text-right font-display" dir="rtl">
      {/* Doctor Header Profile */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-gradient-to-l from-indigo-50/50 via-purple-50/10 to-transparent dark:from-indigo-950/20 dark:via-transparent dark:to-transparent border border-indigo-100/20">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight mb-1 text-slate-800 dark:text-slate-100">
            لوحة تحكم الطبيب المعالج
          </h1>
          <p className="text-muted-foreground text-sm">
            أهلاً بك،{" "}
            <span className="font-bold text-indigo-600 dark:text-indigo-400">
              {currentDoctor ? `د. ${currentDoctor.userName}` : "د. سارة حسن"}
            </span>{" "}
            | {currentDoctor?.specialization || "اختصاصي تعديل السلوك وصعوبات التعلم"}
          </p>
        </div>
        {currentDoctor && (
          <div className="flex items-center gap-2 self-start md:self-center text-xs text-muted-foreground bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 px-3.5 py-1.5 rounded-full shadow-sm">
            <span className="font-medium">{currentDoctor.email}</span>
            <Shield className="w-3.5 h-3.5 text-indigo-500" />
          </div>
        )}
      </div>

      {/* Stats Cards Dashboard */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <StatCard
          title="المرضى المعينون"
          value={totalPatients}
          subtitle={assignedChildren.length > 0 ? "حالات نشطة مخصصة لك" : "إجمالي الحالات المسجلة"}
          icon={<Users className="h-5 w-5" />}
          variant="info"
        />
        <StatCard
          title="إجمالي الجلسات المنجزة"
          value={totalSessions}
          subtitle="خلال الفترات السابقة"
          icon={<Activity className="h-5 w-5" />}
          variant="success"
        />
        <StatCard
          title="متوسط النجاح السريري"
          value={`${avgSuccessRate}%`}
          subtitle="لكافة الجلسات التدريبية"
          icon={<Award className="h-5 w-5" />}
          variant="primary"
        />
      </div>

      {/* Main Sections Layout Grid */}
      <div className="grid gap-6 lg:grid-cols-3">

        {/* Left Side: Assigned Patients List Grid */}
        <div className="lg:col-span-2 space-y-6">
          <SectionCard
            title="قائمة الأطفال المتابعين"
            subtitle="مراقبة الحالة التشخيصية ومستوى استجابة الأطفال للجلسات العلاجية"
          >
            <div className="grid gap-4 md:grid-cols-2">
              {displayChildren.length === 0 ? (
                <div className="col-span-2 text-center py-12 text-muted-foreground">
                  <User className="w-12 h-12 mx-auto mb-2 opacity-30" />
                  <p>لا يوجد أطفال مسجلين حالياً في النظام.</p>
                </div>
              ) : (
                displayChildren.map((child) => {
                  const statusInfo = getStatusDetails(child.status);
                  const childSessions = doctorSessions.filter(s => s.sessionInfo.childId === child.id);

                  return (
                    <Card key={child.id} className="card-base border-slate-100 hover:border-indigo-100/50 hover:shadow-lg transition-all duration-200 overflow-hidden text-right">
                      <CardContent className="p-5 space-y-4">
                        <div className="flex items-center justify-between">
                          <Badge variant={statusInfo.variant} className={statusInfo.className}>
                            {statusInfo.label}
                          </Badge>
                          <div className="flex items-center gap-3">
                            <div className="text-right">
                              <h4 className="font-bold text-slate-800 dark:text-slate-100 leading-tight">
                                {child.name}
                              </h4>
                              <p className="text-xs text-muted-foreground mt-0.5">
                                العمر: {child.age} سنوات | الجنس: {child.gender === "male" ? "ذكر" : "أنثى"}
                              </p>
                            </div>
                            <div className="w-11 h-11 rounded-xl gradient-primary flex items-center justify-center font-bold text-white shadow-sm shadow-indigo-100">
                              {child.avatarInitials || child.name.substring(0, 2)}
                            </div>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 gap-2 text-xs border-t border-b border-slate-50 dark:border-slate-900 py-3 my-2 text-slate-600 dark:text-slate-400">
                          <div className="text-right">
                            <span className="text-muted-foreground">حجم الاضطراب:</span>{" "}
                            <span className="font-semibold text-slate-700 dark:text-slate-200">
                              {getSeverityLabel(child.diagnosisSeverity)}
                            </span>
                          </div>
                          <div className="text-left">
                            <span className="text-muted-foreground">إجمالي الجلسات:</span>{" "}
                            <span className="font-bold text-indigo-600 dark:text-indigo-400">
                              {childSessions.length} جلسة
                            </span>
                          </div>
                        </div>

                        <div className="flex items-center justify-between gap-2 pt-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 font-bold text-xs p-0 h-auto hover:bg-transparent"
                            onClick={() => navigate(`/child-analytics?childId=${child.id}`)}
                          >
                            عرض التحليلات
                            <ChevronRight className="w-3 h-3 mr-0.5 rotate-180" />
                          </Button>
                          <span className="text-[10px] text-muted-foreground flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            تاريخ التسجيل: {child.registeredDate}
                          </span>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })
              )}
            </div>
          </SectionCard>
        </div>

        {/* Right Side: Recent Session Activity Feed */}
        <div className="space-y-6">
          <SectionCard
            title="آخر نشاط للمرضى"
            subtitle="النتائج الفورية لأحدث الجلسات التدريبية المكتملة"
          >
            <div className="space-y-4 max-h-[500px] overflow-y-auto pr-1">
              {sortedSessions.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <Activity className="w-12 h-12 mx-auto mb-2 opacity-30" />
                  <p>لم يتم إجراء أي جلسات تدريبية بعد.</p>
                </div>
              ) : (
                sortedSessions.slice(0, 5).map((session, idx) => {
                  const child = displayChildren.find((c) => c.id === session.sessionInfo.childId);
                  const sessionDate = new Date(session.sessionInfo.startTime);
                  const formattedDate = sessionDate.toLocaleDateString("ar-EG", {
                    month: "short",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  });

                  return (
                    <div
                      key={session.sessionInfo.sessionId || idx}
                      className="flex items-center justify-between p-3.5 border border-slate-100/50 dark:border-slate-800 rounded-xl bg-card hover:bg-slate-50/50 dark:hover:bg-slate-900/50 transition-colors"
                    >
                      <div className="text-right">
                        <div className="font-extrabold text-sm text-indigo-600 dark:text-indigo-400">
                          {session.summary.success_rate}%
                        </div>
                        <div className="text-[10px] text-muted-foreground mt-0.5">
                          {formattedDate}
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="text-right">
                          <h4 className="font-bold text-slate-800 dark:text-slate-100 text-sm">
                            {child ? child.name : "طفل مجهول"}
                          </h4>
                          <p className="text-xs text-muted-foreground mt-0.5">
                            لعب: {session.sessionInfo.game}
                          </p>
                        </div>
                        <div className="w-10 h-10 rounded-xl bg-indigo-50 dark:bg-slate-800 flex items-center justify-center flex-shrink-0 text-indigo-600 dark:text-indigo-400">
                          <Activity className="w-5 h-5" />
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </SectionCard>
        </div>

      </div>
    </div>
  );
}

export default DoctorDashboardPage;
