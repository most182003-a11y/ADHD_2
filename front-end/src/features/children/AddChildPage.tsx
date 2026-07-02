import React, { useState } from "react";
import { Save, ArrowRight, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import SectionCard from "@/components/SectionCard";
import { useToast } from "@/hooks/use-toast";
import { useNavigate } from "react-router-dom";
import { apiClient } from "@/lib/apiClient";
import { useDoctors, useParents } from "@/hooks/useApiData";
import { formatDoctorName } from "@/core/utils/formatters";

export function AddChildPage() {
  const { toast } = useToast();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const { doctors, loading: loadingDoctors } = useDoctors();
  const { parents, loading: loadingParents } = useParents();

  const [formData, setFormData] = useState({
    name: "",
    age: "",
    gender: "male",
    diagnosisSeverity: "moderate",
    doctorId: "none",
    parentId: "none",
    status: "stable"
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const avatarInitials = formData.name
        .split(" ")
        .map(n => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2);

      const genderMap: Record<string, number> = { male: 0, female: 1 };
      const severityMap: Record<string, number> = { mild: 0, moderate: 1, severe: 2 };
      const statusMap: Record<string, number> = { improving: 0, stable: 1, needs_intervention: 2 };

      const payload = {
        name: formData.name,
        age: parseInt(formData.age),
        gender: genderMap[formData.gender] ?? 0,
        diagnosisSeverity: severityMap[formData.diagnosisSeverity] ?? 1,
        status: statusMap[formData.status] ?? 1,
        avatarInitials: avatarInitials,
        doctorId: formData.doctorId === "none" ? null : formData.doctorId,
        parentId: formData.parentId === "none" ? null : formData.parentId
      };

      const resData = await apiClient.post<any>('children', payload);
      if (!resData.succeeded) {
        throw new Error(resData.message || "فشل تسجيل ملف الطفل على الخادم");
      }

      toast({
        title: "تم بنجاح",
        description: "تم تسجيل المريض الجديد بنجاح.",
      });

      navigate("/child-analytics");
    } catch (error: any) {
      console.error("Error adding child:", error);
      toast({
        title: "خطأ",
        description: error.message || "فشل تسجيل المريض.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6" dir="rtl">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
          <ArrowRight size={20} />
        </Button>
        <h2 className="text-xl font-bold font-display text-right">تسجيل طفل مريض جديد</h2>
      </div>

      <SectionCard title="بيانات المريض" subtitle="أدخل تفاصيل الطفل الجديد لتسجيله في النظام">
        <form onSubmit={handleSubmit} className="space-y-4 text-right">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">الاسم الكامل</label>
              <Input 
                required 
                placeholder="مثال: آدم أحمد" 
                value={formData.name}
                onChange={e => setFormData({...formData, name: e.target.value})}
                className="text-right"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">العمر</label>
              <Input 
                required 
                type="number" 
                placeholder="بالسنوات" 
                value={formData.age}
                onChange={e => setFormData({...formData, age: e.target.value})}
                className="text-right"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">الجنس</label>
              <Select value={formData.gender} onValueChange={v => setFormData({...formData, gender: v})}>
                <SelectTrigger className="text-right">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="male" className="text-right">ذكر</SelectItem>
                  <SelectItem value="female" className="text-right">أنثى</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">شدة اضطراب فرط الحركة وتشتت الانتباه (ADHD)</label>
              <Select value={formData.diagnosisSeverity} onValueChange={v => setFormData({...formData, diagnosisSeverity: v})}>
                <SelectTrigger className="text-right">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="mild" className="text-right">بسيط (Mild)</SelectItem>
                  <SelectItem value="moderate" className="text-right">متوسط (Moderate)</SelectItem>
                  <SelectItem value="severe" className="text-right">شديد (Severe)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Parent Selection Dropdown */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground flex items-center gap-1">
                ولي الأمر المرتبط الطفل به
                {loadingParents && <Loader2 size={12} className="animate-spin text-muted-foreground" />}
              </label>
              <Select value={formData.parentId} onValueChange={v => setFormData({...formData, parentId: v})}>
                <SelectTrigger className="border-emerald-500/20 focus:ring-emerald-500/20 text-right">
                  <SelectValue placeholder="اختر حساب ولي الأمر" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none" className="text-right">-- غير معين --</SelectItem>
                  {parents.map(p => (
                    <SelectItem key={p.id} value={p.id} className="text-right">
                      {p.userName} ({p.email})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Doctor Selection Dropdown */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground flex items-center gap-1">
                الطبيب / المعالج المتابع
                {loadingDoctors && <Loader2 size={12} className="animate-spin text-muted-foreground" />}
              </label>
              <Select value={formData.doctorId} onValueChange={v => setFormData({...formData, doctorId: v})}>
                <SelectTrigger className="border-primary/20 focus:ring-primary/20 text-right">
                  <SelectValue placeholder="تعيين طبيب مختص" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none" className="text-right">-- غير معين --</SelectItem>
                  {doctors.map(d => (
                    <SelectItem key={d.id} value={d.id} className="text-right">
                      {formatDoctorName(d.userName)} ({d.specialization || "أخصائي"})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">حالة تقدم الحالة</label>
              <Select value={formData.status} onValueChange={v => setFormData({...formData, status: v})}>
                <SelectTrigger className="text-right">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="improving" className="text-right">يتحسن (Improving)</SelectItem>
                  <SelectItem value="stable" className="text-right">مستقر (Stable)</SelectItem>
                  <SelectItem value="needs_intervention" className="text-right">بحاجة إلى تدخل (Needs Intervention)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="pt-4 flex justify-end">
            <Button type="submit" disabled={loading} className="gradient-primary text-primary-foreground min-w-32">
              <Save size={16} className="ml-2" />
              {loading ? "جاري الحفظ..." : "حفظ ملف المريض"}
            </Button>
          </div>
        </form>
      </SectionCard>
    </div>
  );
}

export default AddChildPage;
