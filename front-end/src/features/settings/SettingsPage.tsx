import { useState } from "react";
import {
  Bell, Moon, Sun, Award, Mail, Phone, Loader2, Trash2
} from "lucide-react";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import SectionCard from "@/components/SectionCard";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";
import { useDoctors, useParents, useChildren, useSessions, ApiResponse } from "@/hooks/useApiData";
import { apiClient } from "@/lib/apiClient";
import { useToast } from "@/hooks/use-toast";
import { useQueryClient } from "@tanstack/react-query";
import { queryKeys } from "@/core/constants/queryKeys";
import { formatDoctorName } from '@/core/utils/formatters';
import { useThemeStore } from "@/core/stores/theme.store";
import { ConfirmDialog } from "@/shared/components/modals/ConfirmDialog";
import { RegisterDoctorForm } from "./components/RegisterDoctorForm";
import { RegisterParentForm } from "./components/RegisterParentForm";

interface SettingsProps {
  darkMode?: boolean;
  onToggleDark?: () => void;
}

const alertRules = [
  { id: 1, label: "مؤشر الاندفاعية > 25", enabled: true },
  { id: 2, label: "معدل النجاح < 60% لثلاث جلسات متتالية", enabled: true },
  { id: 3, label: "التحكم الحركي أقل من 55", enabled: false },
  { id: 4, label: "مؤشر تشتت الانتباه > 30", enabled: true },
  { id: 5, label: "تغيب الطفل عن جلستين أو أكثر", enabled: true },
];

export function SettingsPage({ darkMode: propDarkMode, onToggleDark: propOnToggleDark }: SettingsProps) {
  const queryClient = useQueryClient();
  const storeDarkMode = useThemeStore((state) => state.darkMode);
  const storeToggleDark = useThemeStore((state) => state.toggleDarkMode);

  const darkMode = propDarkMode !== undefined ? propDarkMode : storeDarkMode;
  const onToggleDark = propOnToggleDark || storeToggleDark;

  const { children } = useChildren();
  const { sessions } = useSessions();
  const { role } = useAuth();
  const { toast } = useToast();
  const { doctors, loading: loadingDoctors } = useDoctors();
  const { parents, loading: loadingParents } = useParents();

  const [alerts, setAlerts] = useState(alertRules);
  const [notifEmail, setNotifEmail] = useState(true);
  const [notifInApp, setNotifInApp] = useState(true);

  // Tabs for Admin User Management
  const [activeTab, setActiveTab] = useState<"doctors" | "parents" | "add_doctor" | "add_parent">("doctors");

  // Deletion Confirmation Dialog State
  const [deleteConfirm, setDeleteConfirm] = useState<{
    open: boolean;
    type: "doctor" | "parent" | null;
    id: string | null;
    name: string | null;
  }>({
    open: false,
    type: null,
    id: null,
    name: null
  });
  const [loadingDelete, setLoadingDelete] = useState(false);

  const requestDeleteDoctor = (id: string, name: string) => {
    setDeleteConfirm({
      open: true,
      type: "doctor",
      id,
      name
    });
  };

  const requestDeleteParent = (id: string, name: string) => {
    setDeleteConfirm({
      open: true,
      type: "parent",
      id,
      name
    });
  };

  const executeDelete = async () => {
    if (!deleteConfirm.id || !deleteConfirm.type) return;
    const { id, type, name } = deleteConfirm;
    const formattedName = (name || "").replace(/_/g, " ");

    setLoadingDelete(true);
    try {
      if (type === "doctor") {
        const res = await apiClient.delete<ApiResponse<string>>(`Doctors/${id}`);
        if (!res.succeeded) throw new Error(res.message || "Failed to delete doctor");

        toast({
          title: "تم الحذف بنجاح",
          description: `تم حذف حساب الطبيب د. ${formattedName} وإعادة توجيه الأطفال لجهة معالجة بديلة.`,
        });
      } else {
        const res = await apiClient.delete<ApiResponse<string>>(`Parents/${id}`);
        if (!res.succeeded) throw new Error(res.message || "Failed to delete parent");

        toast({
          title: "تم الحذف بنجاح",
          description: `تم حذف حساب ولي الأمر ${formattedName} وكافة ملفات الأطفال التابعين له بنجاح.`,
        });
      }

      setDeleteConfirm({ open: false, type: null, id: null, name: null });
      queryClient.invalidateQueries({ queryKey: queryKeys.doctors.list() });
      queryClient.invalidateQueries({ queryKey: queryKeys.parents.list() });
    } catch (err: any) {
      toast({
        title: "خطأ أثناء الحذف",
        description: err.message || "فشل إتمام عملية الحذف.",
        variant: "destructive"
      });
    } finally {
      setLoadingDelete(false);
    }
  };

  const toggleAlert = (id: number) => {
    setAlerts(prev => prev.map(a => a.id === id ? { ...a, enabled: !a.enabled } : a));
  };

  return (
    <div className="space-y-6 max-w-3xl">
      {/* Appearance */}
      <SectionCard title="المظهر والسمات" subtitle="تخصيص مظهر وألوان لوحة التحكم">
        <div className="space-y-4">
          <div className="flex items-center justify-between py-2">
            <div className="flex items-center gap-3">
              {darkMode ? <Moon size={18} className="text-primary" /> : <Sun size={18} className="text-primary" />}
              <div className="text-right">
                <p className="text-sm font-medium text-foreground">الوضع الداكن</p>
                <p className="text-xs text-muted-foreground">التبديل بين المظهر الفاتح والمظهر الداكن</p>
              </div>
            </div>
            <Switch checked={darkMode} onCheckedChange={onToggleDark} />
          </div>
        </div>
      </SectionCard>

      {/* Notifications */}
      <SectionCard
        title="التنبيهات والإشعارات"
        subtitle="إعداد قواعد التنبيه وطريقة استلام الإشعارات"
        action={
          <Badge className="status-info text-xs">{alerts.filter(a => a.enabled).length} نشط</Badge>
        }
      >
        <div className="space-y-4">
          <div className="flex items-center justify-between py-2 border-b border-border">
            <div className="flex items-center gap-3">
              <Bell size={18} className="text-primary" />
              <div className="text-right">
                <p className="text-sm font-medium">إشعارات البريد الإلكتروني</p>
                <p className="text-xs text-muted-foreground">تلقي التنبيهات والتقارير عبر البريد</p>
              </div>
            </div>
            <Switch checked={notifEmail} onCheckedChange={setNotifEmail} />
          </div>
          <div className="flex items-center justify-between py-2 border-b border-border">
            <div className="flex items-center gap-3">
              <Bell size={18} className="text-accent" />
              <div className="text-right">
                <p className="text-sm font-medium">الإشعارات داخل النظام</p>
                <p className="text-xs text-muted-foreground">عرض الإشعارات داخل لوحة التحكم</p>
              </div>
            </div>
            <Switch checked={notifInApp} onCheckedChange={setNotifInApp} />
          </div>
          <div className="text-right">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">قواعد وعتبات التنبيه الحرج</p>
            <div className="space-y-2">
              {alerts.map(alert => (
                <div key={alert.id} className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-muted/30 transition-colors">
                  <p className="text-sm text-foreground">{alert.label}</p>
                  <Switch checked={alert.enabled} onCheckedChange={() => toggleAlert(alert.id)} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </SectionCard>

      {/* User & Member Management Dashboard */}
      {role === "Admin" ? (
        <SectionCard
          title="إدارة المستخدمين وفريق العمل"
          subtitle="تسجيل وتحديث وإدارة حسابات الأخصائيين المعالجين وأولياء الأمور"
        >
          <div className="space-y-6">
            {/* Elegant Tab Headers */}
            <div className="flex flex-row-reverse gap-1 p-1 bg-muted/30 border border-border rounded-lg max-w-xl">
              {[
                { id: "doctors", label: `المعالجون (${doctors.length})` },
                { id: "parents", label: `أولياء الأمور (${parents.length})` },
                { id: "add_doctor", label: "تسجيل معالج جديد" },
                { id: "add_parent", label: "تسجيل ولي أمر جديد" },
              ].map(t => (
                <button
                  key={t.id}
                  onClick={() => setActiveTab(t.id as any)}
                  className={cn(
                    "px-4 py-1.5 rounded-md text-xs font-medium transition-all duration-200 flex items-center gap-1.5",
                    activeTab === t.id
                      ? "bg-background text-foreground shadow-sm font-semibold border border-border/40"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted/10"
                  )}
                >
                  {t.label}
                </button>
              ))}
            </div>

            {/* Tab Contents */}
            {activeTab === "doctors" && (
              <div className="space-y-4">
                {loadingDoctors ? (
                  <div className="flex items-center justify-center py-8 text-muted-foreground text-xs gap-2">
                    <Loader2 size={16} className="animate-spin text-primary" />
                    جاري تحميل ملفات الأخصائيين المعالجين...
                  </div>
                ) : doctors.length === 0 ? (
                  <div className="text-center py-8 border border-dashed border-border rounded-xl">
                    <p className="text-sm font-medium text-muted-foreground">لا يوجد أخصائيون معالجون مسجلون حتى الآن.</p>
                    <Button variant="link" size="sm" onClick={() => setActiveTab("add_doctor")} className="text-xs">
                      سجل أول ملف طبيب معالج في النظام
                    </Button>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {doctors.map(doc => (
                      <div key={doc.id} className="relative group border border-border/60 hover:border-primary/30 bg-muted/10 p-4 rounded-xl flex gap-3.5 hover:bg-muted/30 transition-all duration-200">
                        <div className="w-10 h-10 rounded-full gradient-primary flex items-center justify-center flex-shrink-0">
                          <span className="text-xs font-bold text-primary-foreground">
                            {doc.userName.split("_").map(n => n[0]).join("").toUpperCase().slice(0, 2)}
                          </span>
                        </div>
                        <div className="flex-1 min-w-0 text-right">
                          <div className="flex items-start justify-between gap-2">
                            <h4 className="text-sm font-semibold text-foreground truncate">{formatDoctorName(doc.userName)}</h4>
                            <div className="flex items-center gap-1.5">
                              <Badge className="text-[10px] px-2 py-0 gradient-primary border-0 font-normal">أخصائي معالج</Badge>
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-6 w-6 text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-all rounded-md"
                                onClick={() => requestDeleteDoctor(doc.id, doc.userName)}
                                disabled={loadingDelete}
                              >
                                {loadingDelete && deleteConfirm.id === doc.id ? (
                                  <Loader2 size={13} className="animate-spin text-destructive" />
                                ) : (
                                  <Trash2 size={13} />
                                )}
                              </Button>
                            </div>
                          </div>
                          <p className="text-xs text-muted-foreground mt-1 truncate flex items-center gap-1.5">
                            <Award size={12} className="text-primary/70" />
                            {doc.specialization || "أخصائي فرط الحركة وتشتت الانتباه"}
                          </p>
                          <p className="text-xs text-muted-foreground mt-0.5 truncate flex items-center gap-1.5">
                            <Mail size={12} className="text-muted-foreground/75" />
                            {doc.email}
                          </p>
                          {doc.phoneNumber && (
                            <p className="text-[11px] text-muted-foreground mt-0.5 truncate flex items-center gap-1.5">
                              <Phone size={12} className="text-muted-foreground/75" />
                              {doc.phoneNumber}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === "parents" && (
              <div className="space-y-4">
                {loadingParents ? (
                  <div className="flex items-center justify-center py-8 text-muted-foreground text-xs gap-2">
                    <Loader2 size={16} className="animate-spin text-emerald-500" />
                    جاري تحميل ملفات أولياء الأمور...
                  </div>
                ) : parents.length === 0 ? (
                  <div className="text-center py-8 border border-dashed border-border rounded-xl">
                    <p className="text-sm font-medium text-muted-foreground">لا يوجد أولياء أمور مسجلون حتى الآن.</p>
                    <Button variant="link" size="sm" onClick={() => setActiveTab("add_parent")} className="text-xs">
                      سجل أول ولي أمر في النظام
                    </Button>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {parents.map(par => (
                      <div key={par.id} className="relative group border border-border/60 hover:border-emerald-500/30 bg-muted/10 p-4 rounded-xl flex gap-3.5 hover:bg-muted/30 transition-all duration-200">
                        <div className="w-10 h-10 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 flex items-center justify-center flex-shrink-0">
                          <span className="text-xs font-bold">
                            {par.userName.split("_").map(n => n[0]).join("").toUpperCase().slice(0, 2)}
                          </span>
                        </div>
                        <div className="flex-1 min-w-0 text-right">
                          <div className="flex items-start justify-between gap-2">
                            <h4 className="text-sm font-semibold text-foreground truncate">{par.userName.replace(/_/g, " ")}</h4>
                            <div className="flex items-center gap-1.5">
                              <Badge className="text-[10px] px-2 py-0 bg-emerald-500/10 text-emerald-600 hover:bg-emerald-500/20 border-0 font-normal">ولي أمر</Badge>
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-6 w-6 text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-all rounded-md"
                                onClick={() => requestDeleteParent(par.id, par.userName)}
                                disabled={loadingDelete}
                              >
                                {loadingDelete && deleteConfirm.id === par.id ? (
                                  <Loader2 size={13} className="animate-spin text-destructive" />
                                ) : (
                                  <Trash2 size={13} />
                                )}
                              </Button>
                            </div>
                          </div>
                          <p className="text-xs text-muted-foreground mt-2 truncate flex items-center gap-1.5">
                            <Mail size={12} className="text-muted-foreground/75" />
                            {par.email}
                          </p>
                          {par.phoneNumber && (
                            <p className="text-xs text-muted-foreground mt-0.5 truncate flex items-center gap-1.5">
                              <Phone size={12} className="text-muted-foreground/75" />
                              {par.phoneNumber}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === "add_doctor" && (
              <RegisterDoctorForm />
            )}

            {activeTab === "add_parent" && (
              <RegisterParentForm />
            )}
          </div>
        </SectionCard>
      ) : (
        /* Read-only User/Doctor Directory for non-Admins */
        <SectionCard
          title="دليل الأخصائيين والعيادة"
          subtitle="قائمة خبراء الأطفال والمعالجين المتخصصين المسجلين في نظام فرط الحركة وتشتت الانتباه"
        >
          <div className="space-y-4">
            {loadingDoctors ? (
              <div className="flex items-center justify-center py-6 text-muted-foreground text-xs gap-2">
                <Loader2 size={14} className="animate-spin text-primary" />
                جاري تحميل فريق العيادة...
              </div>
            ) : doctors.length === 0 ? (
              <div className="text-center py-6">
                <p className="text-xs text-muted-foreground">لم يتم العثور على أخصائيين في الدليل.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {doctors.map(doc => (
                  <div key={doc.id} className="border border-border/60 bg-muted/10 p-3 rounded-lg flex gap-3 hover:bg-muted/20 transition-all duration-200">
                    <div className="w-8 h-8 rounded-full gradient-primary flex items-center justify-center flex-shrink-0 text-xs font-bold text-primary-foreground">
                      {doc.userName.split("_").map(n => n[0]).join("").toUpperCase().slice(0, 2)}
                    </div>
                    <div className="flex-1 min-w-0 text-right">
                      <h4 className="text-xs font-bold text-foreground">{formatDoctorName(doc.userName)}</h4>
                      <p className="text-[10px] text-muted-foreground flex items-center gap-1 mt-0.5 truncate">
                        <Award size={10} className="text-primary/70" />
                        {doc.specialization || "أخصائي فرط الحركة وتشتت الانتباه"}
                      </p>
                      <p className="text-[10px] text-muted-foreground flex items-center gap-1 truncate">
                        <Mail size={10} />
                        {doc.email}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </SectionCard>
      )}

      {/* System Info */}
      <SectionCard title="معلومات النظام" subtitle="تفاصيل نظام التدريب الذكي لفرط الحركة وتشتت الانتباه">
        <div className="grid grid-cols-2 gap-4 text-sm text-right">
          {[
            { label: "إصدار النظام", value: "v2.5.0 (مباشر)" },
            { label: "آخر تحديث", value: new Date().toLocaleDateString('ar-EG') },
            { label: "حالة قاعدة البيانات", value: "🟢 متصل بالخادم المحلي .NET" },
            { label: "إجمالي الجلسات", value: sessions.length.toString() },
            { label: "إجمالي الأطفال المسجلين", value: children.length.toString() },
            { label: "الترخيص", value: "النسخة الاحترافية للعيادة (نشط)" },
          ].map(({ label, value }) => (
            <div key={label} className="flex flex-col gap-0.5">
              <span className="text-xs text-muted-foreground">{label}</span>
              <span className="font-semibold text-foreground">{value}</span>
            </div>
          ))}
        </div>
      </SectionCard>

      {/* Deletion Dialog */}
      <ConfirmDialog
        isOpen={deleteConfirm.open}
        onOpenChange={(open) => {
          if (!open) setDeleteConfirm({ open: false, type: null, id: null, name: null });
        }}
        title="تأكيد حذف الحساب"
        description={
          deleteConfirm.type === "doctor"
            ? `هل أنت متأكد من حذف الطبيب د. ${(deleteConfirm.name || "").replace(/_/g, " ")}؟ سيقوم النظام تلقائياً بنقل كافة الأطفال التابعين لهذا المعالج إلى أخصائي بديل نشط فور إتمام عملية الحذف لضمان سير العلاج.`
            : `هل أنت متأكد من حذف ولي الأمر ${(deleteConfirm.name || "").replace(/_/g, " ")}؟ تنبيه خطير: حذف ولي الأمر سيؤدي تلقائياً إلى حذف حسابات جميع الأطفال التابعين له وكافة ملفات جلساتهم التدريبية وبيانات التحليل بشكل كامل ونهائي!`
        }
        confirmText={loadingDelete ? "جاري الحذف..." : "تأكيد الحذف"}
        cancelText="إلغاء الأمر"
        onConfirm={executeDelete}
        variant="destructive"
      />
    </div>
  );
}

export default SettingsPage;
