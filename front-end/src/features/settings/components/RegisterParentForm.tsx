import React, { useState } from "react";
import { UserPlus, Loader2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/apiClient";
import { queryKeys } from "@/core/constants/queryKeys";
import { ApiResponse } from "@/hooks/useApiData";

interface RegisterParentFormProps {
  onSuccess?: () => void;
}

export const RegisterParentForm = ({ onSuccess }: RegisterParentFormProps) => {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const [loadingSubmit, setLoadingSubmit] = useState(false);

  const [parentForm, setParentForm] = useState({
    name: "",
    email: "",
    password: "",
    phoneNumber: ""
  });

  const handleRegisterParent = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoadingSubmit(true);
    try {
      const authRes = await apiClient.post<ApiResponse<string>>('Account/register', {
        userName: parentForm.name.toLowerCase().replace(/\s+/g, "_"),
        email: parentForm.email,
        password: parentForm.password,
        role: "Parent",
        phoneNumber: parentForm.phoneNumber || null
      });

      if (!authRes.succeeded) {
        throw new Error(authRes.message || "Failed to create parent account");
      }

      toast({
        title: "تم بنجاح",
        description: `تم تسجيل ولي الأمر ${parentForm.name} وإنشاء حسابه بنجاح.`,
      });

      setParentForm({ name: "", email: "", password: "", phoneNumber: "" });

      queryClient.invalidateQueries({ queryKey: queryKeys.parents.list() });
      if (onSuccess) onSuccess();
    } catch (err: any) {
      toast({
        title: "خطأ في التسجيل",
        description: err.message || "فشل تسجيل حساب ولي الأمر.",
        variant: "destructive"
      });
    } finally {
      setLoadingSubmit(false);
    }
  };

  return (
    <form onSubmit={handleRegisterParent} className="space-y-4 max-w-xl border border-border bg-muted/10 p-5 rounded-xl text-right" dir="rtl">
      <div className="flex items-center gap-2 pb-2 border-b border-border/60">
        <UserPlus size={16} className="text-emerald-500" />
        <h4 className="text-sm font-semibold text-foreground">إضافة ولي أمر جديد</h4>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-muted-foreground">اسم ولي الأمر</label>
          <Input
            required
            placeholder="مثال: أحمد علي"
            value={parentForm.name}
            onChange={e => setParentForm({ ...parentForm, name: e.target.value })}
            className="text-right"
          />
        </div>
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-muted-foreground">البريد الإلكتروني</label>
          <Input
            required
            type="email"
            placeholder="ahmed@example.com"
            value={parentForm.email}
            onChange={e => setParentForm({ ...parentForm, email: e.target.value })}
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
            value={parentForm.password}
            onChange={e => setParentForm({ ...parentForm, password: e.target.value })}
            className="text-right"
          />
        </div>
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-muted-foreground">رقم الهاتف</label>
          <Input
            required
            placeholder="مثال: +201012345678"
            value={parentForm.phoneNumber}
            onChange={e => setParentForm({ ...parentForm, phoneNumber: e.target.value })}
            className="text-right"
          />
        </div>
      </div>

      <div className="pt-2 flex justify-end">
        <Button type="submit" disabled={loadingSubmit} className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs min-w-32">
          {loadingSubmit ? (
            <>
              <Loader2 size={14} className="animate-spin ml-1.5" />
              جاري الحفظ...
            </>
          ) : (
            <>
              <Sparkles size={14} className="ml-1.5" />
              تسجيل حساب ولي الأمر
            </>
          )}
        </Button>
      </div>
    </form>
  );
};

export default RegisterParentForm;
