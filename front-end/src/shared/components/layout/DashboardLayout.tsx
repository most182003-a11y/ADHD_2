import React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { useThemeStore } from "@/core/stores/theme.store";
import { useUIStore } from "@/core/stores/ui.store";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";

interface DashboardLayoutProps {
  children: React.ReactNode;
  darkMode?: boolean;
  onToggleDark?: () => void;
}

export function DashboardLayout({ children, darkMode: propDarkMode, onToggleDark: propOnToggleDark }: DashboardLayoutProps) {
  const storeDarkMode = useThemeStore((state) => state.darkMode);
  const storeToggleDark = useThemeStore((state) => state.toggleDarkMode);
  
  const darkMode = propDarkMode !== undefined ? propDarkMode : storeDarkMode;
  const onToggleDark = propOnToggleDark || storeToggleDark;

  const { 
    sidebarCollapsed: collapsed, 
    toggleSidebar, 
    mobileSidebarOpen: mobileOpen, 
    setMobileSidebarOpen 
  } = useUIStore();

  return (
    <div className={cn("flex h-screen overflow-hidden bg-background", darkMode && "dark")}>
      {/* Desktop Sidebar */}
      <aside className={cn(
        "hidden md:flex flex-col flex-shrink-0 bg-sidebar sidebar-shadow transition-all duration-300 z-20 relative",
        collapsed ? "w-16" : "w-56"
      )}>
        <Sidebar />
        <button
          onClick={toggleSidebar}
          className="absolute -left-3 top-20 w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center shadow-md hover:scale-110 transition-transform z-30"
        >
          {collapsed ? <ChevronLeft size={12} /> : <ChevronRight size={12} />}
        </button>
      </aside>

      {/* Mobile Sidebar Overlay */}
      {mobileOpen && (
        <div className="md:hidden fixed inset-0 z-40 flex">
          <div className="fixed inset-0 bg-black/50" onClick={() => setMobileSidebarOpen(false)} />
          <aside className="relative flex flex-col w-56 bg-sidebar h-full sidebar-shadow z-50">
            <Sidebar />
          </aside>
        </div>
      )}

      {/* Main Content Pane */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header darkMode={darkMode} onToggleDark={onToggleDark} />
        
        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6 animate-fade-in">
          {children}
        </main>
      </div>
    </div>
  );
}

export default DashboardLayout;
