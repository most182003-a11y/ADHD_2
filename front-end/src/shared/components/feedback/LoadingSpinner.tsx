import { Loader2 } from "lucide-react";

interface LoadingSpinnerProps {
  message?: string;
  className?: string;
}

export const LoadingSpinner = ({ message = "جاري التحميل...", className = "" }: LoadingSpinnerProps) => {
  return (
    <div className={`flex flex-col items-center justify-center p-8 space-y-3 ${className}`} dir="rtl">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
      {message && <p className="text-sm text-muted-foreground">{message}</p>}
    </div>
  );
};

export default LoadingSpinner;
