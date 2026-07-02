import React from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { Brain, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";
import { useUIStore } from "@/core/stores/ui.store";
import { routesConfig } from "@/app/routes/routes.config";

export function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { role, logout } = useAuth();
  const { sidebarCollapsed: collapsed, setMobileSidebarOpen } = useUIStore();

  const navItems = routesConfig.filter((item) => item.allowedRoles.includes(role || ""));

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="flex flex-col h-full bg-sidebar">
      {/* Logo */}
      <div className={cn("flex items-center gap-3 px-4 py-5 border-b border-sidebar-border", collapsed && "justify-center px-2")}>
        <div className="flex-shrink-0 w-9 h-9 rounded-xl gradient-primary flex items-center justify-center shadow-lg">
          <Brain className="w-5 h-5 text-primary-foreground" />
        </div>
        {!collapsed && (
          <div className="min-w-0 text-right" dir="rtl">
            <p className="font-display text-sm font-bold text-sidebar-accent-foreground leading-tight">بوابة ADHD</p>
            <p className="text-xs text-sidebar-foreground/60 truncate">تحليلات التقدم</p>
          </div>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
        {navItems.map(({ path, label, icon: Icon }) => {
          const active = location.pathname === path;
          return (
            <NavLink
              key={path}
              to={path}
              onClick={() => setMobileSidebarOpen(false)}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 justify-end text-right",
                active
                  ? "bg-primary text-primary-foreground shadow-md"
                  : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                collapsed && "justify-center px-2"
              )}
            >
              {!collapsed && <span>{label}</span>}
              {Icon && <Icon className="w-4.5 h-4.5 flex-shrink-0" size={18} />}
            </NavLink>
          );
        })}
      </nav>

      {/* Bottom Profile Info */}
      <div className={cn("px-2 py-4 border-t border-sidebar-border", collapsed && "flex flex-col items-center")}>
        <div className={cn("flex items-center gap-2 px-3 py-2 rounded-lg bg-sidebar-accent/50 justify-between w-full", collapsed && "flex-col gap-1 px-2")}>
          <Button variant="ghost" size="icon" className="w-6 h-6 text-sidebar-foreground hover:text-danger" onClick={handleLogout}>
            <LogOut size={14} />
          </Button>
          {!collapsed && (
            <div className="flex-1 min-w-0 text-right" dir="rtl">
              <p className="text-xs font-semibold text-sidebar-accent-foreground truncate">المستخدم الحالي</p>
              <p className="text-xs text-sidebar-foreground/60">
                {role === "Admin" ? "مدير النظام" : role === "Doctor" ? "طبيب مختص" : "ولي أمر"}
              </p>
            </div>
          )}
          <div className="w-7 h-7 rounded-full gradient-primary flex items-center justify-center flex-shrink-0">
            <span className="text-xs font-bold text-primary-foreground">{role ? role.charAt(0) : "U"}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Sidebar;
