import { AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorState = ({ message = "حدث خطأ غير متوقع.", onRetry, className = "" }: ErrorStateProps) => {
  return (
    <div className={`flex flex-col items-center justify-center p-8 text-center space-y-4 border border-destructive/20 bg-destructive/5 rounded-lg ${className}`} dir="rtl">
      <AlertCircle className="h-10 w-10 text-destructive" />
      <div className="space-y-1">
        <h3 className="font-semibold text-destructive">فشلت عملية التحميل</h3>
        <p className="text-sm text-muted-foreground max-w-md">{message}</p>
      </div>
      {onRetry && (
        <Button onClick={onRetry} variant="outline" size="sm" className="border-destructive/30 hover:bg-destructive/10 text-destructive">
          إعادة المحاولة
        </Button>
      )}
    </div>
  );
};

export default ErrorState;
