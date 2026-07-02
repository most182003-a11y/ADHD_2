import { Inbox } from "lucide-react";

interface EmptyStateProps {
  title?: string;
  message?: string;
  className?: string;
}

export const EmptyState = ({ title = "لا توجد بيانات", message = "لا تتوفر أي سجلات حالياً.", className = "" }: EmptyStateProps) => {
  return (
    <div className={`flex flex-col items-center justify-center p-8 text-center space-y-3 border border-dashed rounded-lg ${className}`} dir="rtl">
      <Inbox className="h-10 w-10 text-muted-foreground/60" />
      <div className="space-y-1">
        <h3 className="font-medium text-foreground">{title}</h3>
        <p className="text-sm text-muted-foreground max-w-sm">{message}</p>
      </div>
    </div>
  );
};

export default EmptyState;
