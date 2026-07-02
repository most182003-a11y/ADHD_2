import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { toast } from 'sonner';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      toast.error('يرجى إدخال البريد الإلكتروني وكلمة المرور');
      return;
    }

    setIsLoading(true);
    try {
      await login(email, password);
      
      // Retrieve the decoded role to perform initial routing
      const userStr = localStorage.getItem('adhd_user');
      if (userStr) {
        const user = JSON.parse(userStr);
        const role = user.role;
        const translatedRole = role === 'Admin' ? 'مدير النظام' : role === 'Doctor' ? 'الطبيب' : 'ولي الأمر';
        toast.success(`تم تسجيل الدخول بنجاح بصفتك ${translatedRole}`);
        
        if (role === 'Admin') {
          navigate('/admin');
        } else if (role === 'Doctor') {
          navigate('/doctor');
        } else {
          navigate('/parent');
        }
      } else {
        navigate('/parent');
      }
    } catch (error) {
      const err = error as Error;
      toast.error(err.message || 'فشل تسجيل الدخول. يرجى التحقق من بيانات الاعتماد الخاصة بك.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 p-4" dir="rtl">
      <Card className="w-full max-w-[420px] shadow-xl border-slate-100 bg-white/80 backdrop-blur-md">
        <CardHeader className="space-y-1 text-center">
          <div className="w-12 h-12 bg-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-3 shadow-lg shadow-indigo-200">
            <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <CardTitle className="text-2xl font-bold tracking-tight text-slate-800">نظام ADHD لمتابعة التقدم</CardTitle>
          <CardDescription className="text-slate-500">قم بتسجيل الدخول للوصول إلى لوحة التحكم الخاصة بك</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-1.5 text-right">
              <label className="text-sm font-semibold text-slate-700">البريد الإلكتروني</label>
              <Input 
                type="email" 
                placeholder="admin@adhd.com" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="border-slate-200 focus-visible:ring-indigo-500 text-right"
                disabled={isLoading}
              />
            </div>
            <div className="space-y-1.5 text-right">
              <label className="text-sm font-semibold text-slate-700">كلمة المرور</label>
              <Input 
                type="password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="border-slate-200 focus-visible:ring-indigo-500 text-right"
                disabled={isLoading}
                placeholder="••••••••"
              />
            </div>
            <Button type="submit" className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 transition-all shadow-md shadow-indigo-100" disabled={isLoading}>
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  جاري التحقق...
                </span>
              ) : 'تسجيل الدخول'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

export default LoginPage;
