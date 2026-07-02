import React from "react";
import { LayoutDashboard, Users, Gamepad2, FileText, Settings, UserPlus } from "lucide-react";

export interface RouteConfig {
  path: string;
  label: string;
  icon?: React.ComponentType<any>;
  allowedRoles: string[];
  elementName: string; // Used to lazily resolve or reference page components
}

export const routesConfig: RouteConfig[] = [
  {
    path: "/admin",
    label: "نظرة عامة",
    icon: LayoutDashboard,
    allowedRoles: ["Admin"],
    elementName: "Overview"
  },
  {
    path: "/doctor",
    label: "لوحة الطبيب",
    icon: LayoutDashboard,
    allowedRoles: ["Doctor"],
    elementName: "DoctorDashboard"
  },
  {
    path: "/parent",
    label: "لوحة ولي الأمر",
    icon: LayoutDashboard,
    allowedRoles: ["Parent"],
    elementName: "ParentDashboard"
  },
  {
    path: "/games",
    label: "دليل الألعاب العلاجية",
    icon: Gamepad2,
    allowedRoles: ["Admin", "Doctor"],
    elementName: "GamesCatalog"
  },
  {
    path: "/child-analytics",
    label: "تحليلات الأطفال",
    icon: Users,
    allowedRoles: ["Admin", "Doctor"],
    elementName: "ChildAnalytics"
  },
  {
    path: "/add-child",
    label: "إضافة طفل / مريض",
    icon: UserPlus,
    allowedRoles: ["Admin", "Doctor"],
    elementName: "AddChild"
  },
  {
    path: "/game-analytics",
    label: "تحليلات الألعاب المتقدمة",
    icon: Gamepad2,
    allowedRoles: ["Admin"],
    elementName: "GameAnalytics"
  },
  {
    path: "/reports",
    label: "التقارير الطبية",
    icon: FileText,
    allowedRoles: ["Admin", "Doctor"],
    elementName: "Reports"
  },
  {
    path: "/settings",
    label: "إعدادات النظام",
    icon: Settings,
    allowedRoles: ["Admin", "Doctor", "Parent"],
    elementName: "Settings"
  }
];
