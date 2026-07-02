import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface SectionCardProps {
  title?: string;
  subtitle?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
  noPadding?: boolean;
}

export default function SectionCard({ title, subtitle, action, children, className, noPadding }: SectionCardProps) {
  const hasHeader = title || subtitle || action;

  return (
    <div className={cn("bg-card rounded-xl border border-border card-base flex flex-col", className)}>
      {hasHeader && (
        <div className="flex items-center justify-between px-5 py-4 border-b border-border">
          <div>
            {title && <h3 className="font-display text-sm font-semibold text-foreground">{title}</h3>}
            {subtitle && <p className="text-xs text-muted-foreground mt-0.5">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div className={cn("flex-1", !noPadding && "p-5")}>
        {children}
      </div>
    </div>
  );
}

