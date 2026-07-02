import React, { useState } from "react";
import { UserPlus, Loader2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/apiClient";
import { queryKeys } from "@/core/constants/queryKeys";
import { ApiResponse } from "@/hooks/useApiData";

interface RegisterDoctorFormProps {
  onSuccess?: () => void;
}

export const RegisterDoctorForm = ({ onSuccess }: RegisterDoctorFormProps) => {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const [loadingSubmit, setLoadingSubmit] = useState(false);
  
  const [doctorForm, setDoctorForm] = useState({
    name: "",
    email: "",
    password: "",
    phoneNumber: "",
    specialization: ""
  });

  const handleRegisterDoctor = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoadingSubmit(true);
    try {
      const authRes = await apiClient.post<ApiResponse<string>>('Account/register', {
        userName: doctorForm.name.toLowerCase().replace(/\s+/g, "_"),
        email: doctorForm.email,
        password: doctorForm.password,
        role: "Doctor",
        phoneNumber: doctorForm.phoneNumber || null,
        specialization: doctorForm.specialization || null
      });

      if (!authRes.succeeded) {
        throw new Error(authRes.message || "Failed to create doctor account");
      }

      toast({
        title: "تم بنجاح",
        description: `تم تسجيل الطبيب المعالج د. ${doctorForm.name} وإنشاء حسابه بنجاح.`,
      });

      setDoctorForm({ name: "", email: "", password: "", phoneNumber: "", specialization: "" });
      queryClient.invalidateQueries({ queryKey: queryKeys.doctors.list() });
      if (onSuccess) onSuccess();
    } catch (err: any) {
      toast({
        title: "خطأ في التسجيل",
        description: err.message || "فشل تسجيل حساب المعالج.",
        variant: "destructive"
      });
    } finally {
      setLoadingSubmit(false);
    }
  };

  return (
    <form onSubmit={handleRegisterDoctor} className="space-y-4 max-w-xl border border-border bg-muted/10 p-5 rounded-xl text-right" dir="rtl">
      <div className="flex items-center gap-2 pb-2 border-b border-border/60">
        <UserPlus size={16} className="text-primary" />
        <h4 className="text-sm font-semibold text-foreground">إضافة أخصائي معالج جديد</h4>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-muted-foreground">الاسم الكامل</label>
          <Input
            required
            placeholder="مثال: د. سارة حسن"
            value={doctorForm.name}
            onChange={e => setDoctorForm({ ...doctorForm, name: e.target.value })}
            className="text-right"
          />
        </div>
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-muted-foreground">البريد الإلكتروني</label>
          <Input
            required
            type="email"
            placeholder="sara@example.com"
            value={doctorForm.email}
            onChange={e => setDoctorForm({ ...doctorForm, email: e.target.value })}
            className="text-right"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-muted-foreground">كلمة مرور الحساب</label>
          <Input
            required
            type="password"
            placeholder="••••••••"
            value={doctorForm.password}
            onChange={e => setDoctorForm({ ...doctorForm, password: e.target.value })}
            className="text-right"
          />
        </div>
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-muted-foreground">التخصص</label>
          <Input
            placeholder="مثال: العلاج السلوكي المعرفي"
            value={doctorForm.specialization}
            onChange={e => setDoctorForm({ ...doctorForm, specialization: e.target.value })}
            className="text-right"
          />
        </div>
      </div>

      <div className="space-y-1.5">
        <label className="text-xs font-semibold text-muted-foreground">رقم الهاتف</label>
        <Input
          required
          placeholder="مثال: +966 50 000 0000"
          value={doctorForm.phoneNumber}
          onChange={e => setDoctorForm({ ...doctorForm, phoneNumber: e.target.value })}
          className="text-right"
        />
      </div>

      <div className="pt-2 flex justify-end">
        <Button type="submit" disabled={loadingSubmit} className="gradient-primary text-primary-foreground text-xs min-w-32">
          {loadingSubmit ? (
            <>
              <Loader2 size={14} className="animate-spin ml-1.5" />
              جاري الحفظ...
            </>
          ) : (
            <>
              <Sparkles size={14} className="ml-1.5" />
              تسجيل حساب المعالج
            </>
          )}
        </Button>
      </div>
    </form>
  );
};

export default RegisterDoctorForm;
