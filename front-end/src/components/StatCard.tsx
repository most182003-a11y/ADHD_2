import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: ReactNode;
  trend?: { value: number; positive: boolean };
  variant?: "primary" | "amber" | "success" | "danger" | "info";
  className?: string;
}

const variantStyles = {
  primary: "gradient-primary text-primary-foreground",
  amber: "gradient-amber text-accent-foreground",
  success: "gradient-success text-primary-foreground",
  danger: "bg-danger text-primary-foreground",
  info: "bg-info text-primary-foreground",
};

const iconBg = {
  primary: "bg-primary-foreground/20",
  amber: "bg-accent-foreground/10",
  success: "bg-primary-foreground/20",
  danger: "bg-primary-foreground/20",
  info: "bg-primary-foreground/20",
};

export default function StatCard({ title, value, subtitle, icon, trend, variant = "primary", className }: StatCardProps) {
  return (
    <div className={cn("rounded-xl p-5 card-elevated flex flex-col gap-3", variantStyles[variant], className)}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium opacity-85">{title}</p>
          <p className="text-3xl font-display font-bold mt-1">{value}</p>
          {subtitle && <p className="text-xs opacity-70 mt-0.5">{subtitle}</p>}
        </div>
        <div className={cn("w-11 h-11 rounded-xl flex items-center justify-center", iconBg[variant])}>
          {icon}
        </div>
      </div>
      {trend && (
        <div className="flex items-center gap-1.5">
          <span className={cn("text-xs font-semibold", trend.positive ? "opacity-100" : "opacity-80")}>
            {trend.positive ? "↑" : "↓"} {Math.abs(trend.value)}%
          </span>
          <span className="text-xs opacity-70">vs last month</span>
        </div>
      )}
    </div>
  );
}
