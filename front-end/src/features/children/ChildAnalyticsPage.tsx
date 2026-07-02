import React, { useState, useMemo, useEffect } from "react";
import { severityMapArabic } from "@/core/utils/translators";
import { Target, TrendingUp, Clock, Zap } from "lucide-react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Legend
} from "recharts";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import SectionCard from "@/components/SectionCard";
import StatCard from "@/components/StatCard";
import { cn } from "@/lib/utils";
import { useChildren, useSessions, useDoctors } from "@/hooks/useApiData";
import { Skeleton } from "@/components/ui/skeleton";
import { targets } from "@/lib/data-utils";
import { useToast } from "@/hooks/use-toast";
import { useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/core/constants/queryKeys";
import { apiClient } from "@/lib/apiClient";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { formatDoctorName } from '@/core/utils/formatters';
import { CustomTooltip } from "@/shared/components/data-display/CustomTooltip";

const MetricBadge = ({ value, target, unit = "", higherBetter = true }: { value: number, target: number, unit?: string, higherBetter?: boolean }) => {
  const good = higherBetter ? value >= target : value <= target;
  return (
    <span className={cn("text-xs font-semibold px-2 py-0.5 rounded-full", good ? "status-success" : "status-danger")}>
      {value.toFixed(2)}{unit}
    </span>
  );
};

export function ChildAnalyticsPage() {
  const queryClient = useQueryClient();
  const { children, loading: loadingChildren } = useChildren();
  const { doctors } = useDoctors();
  const { toast } = useToast();
  const [selectedId, setSelectedId] = useState<string | undefined>(undefined);

  // Edit child modal state
  const [isEditing, setIsEditing] = useState(false);
  const [loadingEdit, setLoadingEdit] = useState(false);
  const [editForm, setEditForm] = useState({
    name: "",
    age: 0,
    gender: "male",
    diagnosisSeverity: "moderate",
    status: "stable",
    doctorId: ""
  });

  // Set default selectedId when children are loaded
  useEffect(() => {
    if (children.length > 0 && !selectedId) {
      setSelectedId(children[0].id);
    }
  }, [children, selectedId]);

  const { sessions, loading: loadingSessions } = useSessions(selectedId || undefined);

  const child = useMemo(() => children.find(c => c.id === selectedId), [children, selectedId]);

  // Set edit form values when child is loaded/changed
  useEffect(() => {
    if (child) {
      setEditForm({
        name: child.name,
        age: child.age,
        gender: child.gender || "male",
        diagnosisSeverity: child.diagnosisSeverity || "moderate",
        status: child.status || "stable",
        doctorId: child.doctorId || ""
      });
    }
  }, [child]);

  const handleUpdateChild = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!child) return;
    setLoadingEdit(true);
    const genderMap: Record<string, number> = { male: 0, female: 1 };
    const severityMap: Record<string, number> = { mild: 0, moderate: 1, severe: 2 };
    const statusMap: Record<string, number> = { improving: 0, stable: 1, needs_intervention: 2 };

    try {
      const res = await apiClient.put<{ succeeded: boolean; message?: string }>(`Children/${child.id}`, {
        id: child.id,
        name: editForm.name,
        age: Number(editForm.age),
        gender: genderMap[editForm.gender] ?? 0,
        diagnosisSeverity: severityMap[editForm.diagnosisSeverity] ?? 1,
        status: statusMap[editForm.status] ?? 1,
        doctorId: editForm.doctorId || null,
        parentId: child.parentId
      });

      if (!res.succeeded) throw new Error(res.message || "Failed to update child profile");

      toast({
        title: "تم تحديث البيانات",
        description: `تم تحديث ملف الطفل ${editForm.name} بنجاح.`,
      });
      setIsEditing(false);
      queryClient.invalidateQueries({ queryKey: queryKeys.children.list() });
    } catch (err: any) {
      toast({
        title: "فشل التحديث",
        description: err.message || "فشل تحديث بيانات الطفل.",
        variant: "destructive"
      });
    } finally {
      setLoadingEdit(false);
    }
  };

  const lastSession = sessions.length > 0 ? sessions[0] : null;

  const chartData = useMemo(() =>
    sessions.map((s, i) => ({
      session: `ج${i + 1}`,
      impulsivity: s.summary.impulsivity_index,
      motor: s.summary.motor_control_score,
      distraction: s.summary.distraction_score,
      reaction: s.summary.avg_reaction_time * 100, // scale for chart
      success: s.summary.success_rate,
    })), [sessions]);

  const radarData = lastSession ? [
    { metric: "معدل النجاح", actual: lastSession.summary.success_rate, target: targets.success_rate },
    { metric: "التحكم الحركي", actual: lastSession.summary.motor_control_score, target: targets.motor_control_score },
    { metric: "الاندفاعية (عكسي)", actual: 100 - lastSession.summary.impulsivity_index * 4, target: 100 - targets.impulsivity_index * 4 },
    { metric: "التركيز (عكسي)", actual: 100 - lastSession.summary.distraction_score * 4, target: 100 - targets.distraction_score * 4 },
    { metric: "الاستجابة (عكسي)", actual: 100 - lastSession.summary.avg_reaction_time * 80, target: 100 - targets.avg_reaction_time * 80 },
  ] : [];

  const STATUS_LABELS: Record<string, { label: string; cls: string }> = {
    improving: { label: "يتحسن", cls: "status-success" },
    stable: { label: "مستقر", cls: "status-warning" },
    needs_intervention: { label: "بحاجة لتدخل", cls: "status-danger" },
  };

  const severityMapArabicLocal = (sev: string) => severityMapArabic(sev, 'masculine');

  if (loadingChildren || (selectedId && loadingSessions)) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64 rounded-lg" />
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-32 w-full rounded-xl" />)}
        </div>
        <Skeleton className="h-[400px] w-full rounded-xl" />
      </div>
    );
  }

  if (!child || !lastSession) return (
    <div className="space-y-6" dir="rtl">
       <Select value={selectedId || ""} onValueChange={setSelectedId}>
          <SelectTrigger className="w-64">
            <SelectValue placeholder="اختر الطفل المريض..." />
          </SelectTrigger>
          <SelectContent>
            {children.map(c => (
              <SelectItem key={c.id} value={c.id}>
                <div className="flex items-center gap-2">
                  <span className="font-medium">{c.name}</span>
                  <span className="text-muted-foreground text-xs">العمر: {c.age} سنوات</span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <div className="text-muted-foreground p-8 text-center border border-dashed rounded-xl">لا توجد بيانات جلسات مسجلة لهذا الطفل حالياً.</div>
    </div>
  );

  const st = STATUS_LABELS[child.status] || STATUS_LABELS.stable;

  return (
    <div className="space-y-6" dir="rtl">
      {/* Child Selector */}
      <div className="flex flex-wrap items-center gap-4">
        <Select value={selectedId} onValueChange={setSelectedId}>
          <SelectTrigger className="w-64">
            <SelectValue placeholder="اختر الطفل المريض..." />
          </SelectTrigger>
          <SelectContent>
            {children.map(c => (
              <SelectItem key={c.id} value={c.id}>
                <div className="flex items-center gap-2">
                  <span className="font-medium">{c.name}</span>
                  <span className="text-muted-foreground text-xs">العمر: {c.age} سنوات</span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full gradient-primary flex items-center justify-center">
            <span className="text-sm font-bold text-primary-foreground">{child.avatarInitials}</span>
          </div>
          <div className="text-right">
            <p className="font-semibold text-foreground">{child.name}</p>
            <p className="text-xs text-muted-foreground">العمر: {child.age} سنوات · تشخيص {severityMapArabicLocal(child.diagnosisSeverity)} · {sessions.length} جلسة تدريبية</p>
          </div>
          <Badge className={cn("text-xs", st.cls)}>{st.label}</Badge>
          <Button 
            variant="outline" 
            size="sm" 
            className="h-8 text-xs font-semibold mr-2 border-primary/20 text-primary hover:bg-primary/5 hover:text-primary transition-all duration-200"
            onClick={() => setIsEditing(true)}
          >
            تعديل بيانات الطفل
          </Button>
        </div>
      </div>

      {/* Edit Child Modal Overlay */}
      {isEditing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-fade-in" dir="rtl">
          <div className="bg-card border border-border rounded-2xl w-full max-w-lg p-6 shadow-2xl relative space-y-4 text-right">
            <h3 className="text-lg font-bold text-foreground border-b border-border pb-3">تعديل ملف وتعيين الطبيب للطفل {child.name}</h3>
            
            <form onSubmit={handleUpdateChild} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground">اسم الطفل</label>
                  <Input
                    required
                    value={editForm.name}
                    onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                    className="text-right"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground">العمر (بالسنوات)</label>
                  <Input
                    required
                    type="number"
                    value={editForm.age}
                    onChange={(e) => setEditForm({ ...editForm, age: Number(e.target.value) })}
                    className="text-right"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground">الجنس</label>
                  <select
                    className="w-full text-right p-2 border border-border rounded-lg bg-background text-sm"
                    value={editForm.gender}
                    onChange={(e) => setEditForm({ ...editForm, gender: e.target.value })}
                  >
                    <option value="male">ذكر</option>
                    <option value="female">أنثى</option>
                  </select>
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground">درجة التشخيص</label>
                  <select
                    className="w-full text-right p-2 border border-border rounded-lg bg-background text-sm"
                    value={editForm.diagnosisSeverity}
                    onChange={(e) => setEditForm({ ...editForm, diagnosisSeverity: e.target.value })}
                  >
                    <option value="mild">بسيط</option>
                    <option value="moderate">متوسط</option>
                    <option value="severe">شديد</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground">حالة التقدم</label>
                  <select
                    className="w-full text-right p-2 border border-border rounded-lg bg-background text-sm"
                    value={editForm.status}
                    onChange={(e) => setEditForm({ ...editForm, status: e.target.value })}
                  >
                    <option value="stable">مستقر</option>
                    <option value="improving">يتحسن</option>
                    <option value="needs_intervention">بحاجة لتدخل</option>
                  </select>
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-muted-foreground">الطبيب المعالج الخاص بالطفل</label>
                  <select
                    className="w-full text-right p-2 border border-border rounded-lg bg-background text-sm text-primary font-semibold"
                    value={editForm.doctorId}
                    onChange={(e) => setEditForm({ ...editForm, doctorId: e.target.value })}
                  >
                    <option value="">لا يوجد معالج حالياً</option>
                    {doctors.map((d) => (
                      <option key={d.id} value={d.id}>
                        {formatDoctorName(d.userName)}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-border mt-4">
                <Button type="button" variant="outline" className="text-xs" onClick={() => setIsEditing(false)}>
                  إلغاء
                </Button>
                <Button type="submit" disabled={loadingEdit} className="gradient-primary text-primary-foreground text-xs min-w-[100px]">
                  {loadingEdit ? "جاري الحفظ..." : "حفظ التعديلات"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Quick Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="معدل النجاح" value={`${lastSession.summary.success_rate.toFixed(1)}%`} subtitle="آخر جلسة" icon={<TrendingUp size={18} />} variant="primary" />
        <StatCard title="التحكم الحركي" value={`${lastSession.summary.motor_control_score.toFixed(1)}`} subtitle="درجة الجلسة الأخيرة" icon={<Target size={18} />} variant="success" />
        <StatCard title="مؤشر الاندفاعية" value={`${lastSession.summary.impulsivity_index.toFixed(1)}`} subtitle="المؤشر (الأقل أفضل)" icon={<Zap size={18} />} variant="amber" />
        <StatCard title="زمن الاستجابة" value={`${(lastSession.summary.avg_reaction_time * 1000).toFixed(0)} ملي ثانية`} subtitle="متوسط سرعة البديهة" icon={<Clock size={18} />} variant="info" />
      </div>

      {/* Multi-line Chart */}
      <SectionCard title="تقدم الحالة عبر الجلسات" subtitle="مؤشرات الأداء الرئيسية عبر كافة الجلسات">
        <div className="flex flex-wrap gap-4 mb-4 text-xs">
          {[
            { color: "#dc2626", label: "مؤشر الاندفاعية" },
            { color: "#16a34a", label: "التحكم الحركي" },
            { color: "#d97706", label: "مؤشر التشتت" },
            { color: "#0284c7", label: "زمن الاستجابة (×100)" },
          ].map(({ color, label }) => (
            <div key={label} className="flex items-center gap-1.5 text-right">
              <span className="w-3 h-0.5 rounded" style={{ background: color }} />
              <span className="text-muted-foreground">{label}</span>
            </div>
          ))}
        </div>
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={chartData} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
            <XAxis dataKey="session" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip content={<CustomTooltip labelPrefix="الجلسة " />} />
            <Line type="monotone" dataKey="impulsivity" name="مؤشر الاندفاعية" stroke="#dc2626" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="motor" name="التحكم الحركي" stroke="#16a34a" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="distraction" name="مؤشر التشتت" stroke="#d97706" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="reaction" name="زمن الاستجابة ×100" stroke="#0284c7" strokeWidth={2} dot={false} strokeDasharray="4 2" />
          </LineChart>
        </ResponsiveContainer>
      </SectionCard>

      {/* Radar + Last Session Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SectionCard title="المستهدف مقابل الفعلي" subtitle="مخطط رادار يقارن أداء الجلسة الأخيرة بالحد الأقصى المرجو">
          <ResponsiveContainer width="100%" height={240}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="metric" tick={{ fontSize: 10 }} />
              <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fontSize: 9 }} />
              <Radar name="الفعلي" dataKey="actual" stroke="hsl(193,72%,28%)" fill="hsl(193,72%,28%)" fillOpacity={0.25} />
              <Radar name="المستهدف" dataKey="target" stroke="hsl(38,93%,52%)" fill="hsl(38,93%,52%)" fillOpacity={0.15} />
              <Legend iconType="circle" iconSize={8} formatter={(v) => <span className="text-xs text-foreground">{v}</span>} />
            </RadarChart>
          </ResponsiveContainer>
        </SectionCard>

        <SectionCard title="تفاصيل الجلسة الأخيرة" subtitle={`الجلسة رقم ${lastSession.sessionInfo.sessionId}`}>
          <div className="space-y-3">
            {[
              { label: "معدل النجاح", value: lastSession.summary.success_rate, target: targets.success_rate, unit: "%", higherBetter: true },
              { label: "درجة التحكم الحركي", value: lastSession.summary.motor_control_score, target: targets.motor_control_score, unit: "", higherBetter: true },
              { label: "مؤشر الاندفاعية", value: lastSession.summary.impulsivity_index, target: targets.impulsivity_index, unit: "", higherBetter: false },
              { label: "درجة التشتت", value: lastSession.summary.distraction_score, target: targets.distraction_score, unit: "", higherBetter: false },
              { label: "متوسط زمن الاستجابة", value: lastSession.summary.avg_reaction_time, target: targets.avg_reaction_time, unit: " ثانية", higherBetter: false },
              { label: "إجمالي المحاولات", value: lastSession.summary.total_trials, target: 20, unit: "", higherBetter: true },
              { label: "أقصى نجاح متتالي", value: lastSession.summary.max_consecutive_success, target: 8, unit: "", higherBetter: true },
            ].map(row => (
              <div key={row.label} className="flex items-center justify-between text-right">
                <span className="text-sm text-muted-foreground">{row.label}</span>
                <div className="flex items-center gap-2">
                  <MetricBadge value={row.value} target={row.target} unit={row.unit} higherBetter={row.higherBetter} />
                  <span className="text-xs text-muted-foreground">/ {row.target}{row.unit}</span>
                </div>
              </div>
            ))}
          </div>
        </SectionCard>
      </div>

      {/* Sessions Table */}
      <SectionCard title="سجل كافة الجلسات" subtitle={`إجمالي التدريبات: ${sessions.length} جلسة`} noPadding>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-muted/20">
                {["#", "التاريخ", "المدة", "المحاولات", "معدل النجاح", "الاندفاعية", "التحكم", "التشتت", "زمن الاستجابة"].map(h => (
                  <th key={h} className="text-right px-4 py-3 text-xs font-bold text-muted-foreground whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {sessions.map((s, i) => (
                <tr key={s.sessionInfo.sessionId} className="hover:bg-muted/40 transition-colors text-right">
                  <td className="px-4 py-2.5 text-muted-foreground text-xs">{i + 1}</td>
                  <td className="px-4 py-2.5 whitespace-nowrap text-xs">{new Date(s.sessionInfo.startTime).toLocaleDateString('ar-EG')}</td>
                  <td className="px-4 py-2.5 text-xs">{s.sessionInfo.durationMinutes} دقيقة</td>
                  <td className="px-4 py-2.5 text-xs">{s.summary.total_trials}</td>
                  <td className="px-4 py-2.5">
                    <span className={cn("text-xs font-semibold", s.summary.success_rate >= 80 ? "text-success" : "text-danger")}>
                      {s.summary.success_rate.toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-xs">{s.summary.impulsivity_index.toFixed(1)}</td>
                  <td className="px-4 py-2.5 text-xs">{s.summary.motor_control_score.toFixed(1)}</td>
                  <td className="px-4 py-2.5 text-xs">{s.summary.distraction_score.toFixed(1)}</td>
                  <td className="px-4 py-2.5 text-xs">{(s.summary.avg_reaction_time * 1000).toFixed(0)} ملي ثانية</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </SectionCard>
    </div>
  );
}

export default ChildAnalyticsPage;
