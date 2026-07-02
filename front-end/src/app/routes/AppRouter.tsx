import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import DashboardLayout from "@/shared/components/layout/DashboardLayout";
import ProtectedRoute from "./ProtectedRoute";
import ErrorBoundary from "@/shared/components/feedback/ErrorBoundary";
import { useAuth } from "@/hooks/useAuth";

// Pages
import Overview from "@/pages/Overview";
import ChildAnalytics from "@/pages/ChildAnalytics";
import GameAnalytics from "@/pages/GameAnalytics";
import Reports from "@/pages/Reports";
import AddChild from "@/pages/AddChild";
import Settings from "@/pages/Settings";
import NotFound from "@/pages/NotFound";
import Login from "@/pages/Login";
import DoctorDashboard from "@/pages/DoctorDashboard";
import ParentDashboard from "@/pages/ParentDashboard";
import GamesCatalog from "@/pages/GamesCatalog";

export function AppRouter() {
  const { isAuthenticated } = useAuth();
  
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      
      {/* Protected Routes inside Dashboard Layout */}
      <Route element={
        isAuthenticated ? (
          <DashboardLayout>
            <Routes>
              <Route path="/admin" element={<ProtectedRoute allowedRoles={["Admin"]}><ErrorBoundary><Overview /></ErrorBoundary></ProtectedRoute>} />
              <Route path="/doctor" element={<ProtectedRoute allowedRoles={["Doctor"]}><ErrorBoundary><DoctorDashboard /></ErrorBoundary></ProtectedRoute>} />
              <Route path="/parent" element={<ProtectedRoute allowedRoles={["Parent"]}><ErrorBoundary><ParentDashboard /></ErrorBoundary></ProtectedRoute>} />
              <Route path="/games" element={<ProtectedRoute allowedRoles={["Admin", "Doctor"]}><ErrorBoundary><GamesCatalog /></ErrorBoundary></ProtectedRoute>} />
              <Route path="/child-analytics" element={<ProtectedRoute allowedRoles={["Admin", "Doctor"]}><ErrorBoundary><ChildAnalytics /></ErrorBoundary></ProtectedRoute>} />
              <Route path="/add-child" element={<ProtectedRoute allowedRoles={["Admin", "Doctor"]}><ErrorBoundary><AddChild /></ErrorBoundary></ProtectedRoute>} />
              <Route path="/game-analytics" element={<ProtectedRoute allowedRoles={["Admin"]}><ErrorBoundary><GameAnalytics /></ErrorBoundary></ProtectedRoute>} />
              <Route path="/reports" element={<ProtectedRoute allowedRoles={["Admin", "Doctor"]}><ErrorBoundary><Reports /></ErrorBoundary></ProtectedRoute>} />
              <Route path="/settings" element={<ProtectedRoute><ErrorBoundary><Settings /></ErrorBoundary></ProtectedRoute>} />
              
              {/* Default redirects */}
              <Route path="/" element={<ProtectedRoute><ErrorBoundary><Overview /></ErrorBoundary></ProtectedRoute>} /> 
              <Route path="*" element={<NotFound />} />
            </Routes>
          </DashboardLayout>
        ) : (
          <Navigate to="/login" replace />
        )
      }>
        <Route path="/*" element={null} />
      </Route>
    </Routes>
  );
}

export default AppRouter;

