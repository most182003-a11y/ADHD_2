import React from "react";
import { BrowserRouter } from "react-router-dom";
import { Loader2 } from "lucide-react";
import { AppProviders } from "./app/providers/AppProviders";
import { AppRouter } from "./app/routes/AppRouter";
import { useAuth } from "@/hooks/useAuth";

function AppContent() {
  const { isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return <AppRouter />;
}

export function App() {
  return (
    <AppProviders>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </AppProviders>
  );
}

export default App;
