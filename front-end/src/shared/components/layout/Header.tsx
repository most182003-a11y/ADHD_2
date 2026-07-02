import React from "react";
import { useLocation } from "react-router-dom";
import { Menu, X, Sun, Moon, Bell } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useUIStore } from "@/core/stores/ui.store";
import { routesConfig } from "@/app/routes/routes.config";

interface HeaderProps {
  darkMode: boolean;
  onToggleDark: () => void;
}

export function Header({ darkMode, onToggleDark }: HeaderProps) {
  const location = useLocation();
  const { mobileSidebarOpen: mobileOpen, toggleMobileSidebar } = useUIStore();

  const currentNav = routesConfig.find((n) => n.path === location.pathname);

  return (
    <header className="h-14 flex items-center gap-3 px-4 md:px-6 bg-card border-b border-border flex-shrink-0 card-base w-full">
      <button className="md:hidden p-1.5 rounded-lg hover:bg-muted" onClick={toggleMobileSidebar}>
        {mobileOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Breadcrumb / Title */}
      <div className="flex-1 min-w-0 text-right" dir="rtl">
        <h1 className="font-display text-base font-semibold text-foreground truncate">
          {currentNav?.label || "لوحة التحكم"}
        </h1>
        <p className="text-xs text-muted-foreground hidden sm:block">
          نظام التحليل والتدريب الذكي لاضطراب فرط الحركة وتشتت الانتباه
        </p>
      </div>

      {/* Action utilities */}
      <div className="flex items-center gap-2">
        <Badge variant="secondary" className="hidden sm:flex text-xs font-medium">
          <span className="w-1.5 h-1.5 rounded-full bg-success ml-1.5 animate-pulse-soft" />
          متصل
        </Badge>
        <Button variant="ghost" size="icon" className="w-8 h-8 relative">
          <Bell size={16} />
          <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-danger" />
        </Button>
        <Button variant="ghost" size="icon" onClick={onToggleDark} className="w-8 h-8">
          {darkMode ? <Sun size={16} /> : <Moon size={16} />}
        </Button>
      </div>
    </header>
  );
}

export default Header;
