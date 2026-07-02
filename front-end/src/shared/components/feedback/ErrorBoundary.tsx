import React, { Component, ErrorInfo, ReactNode } from "react";
import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error in boundary:", error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.href = "/";
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-background text-foreground" dir="rtl">
          <div className="max-w-md w-full text-center space-y-6 p-8 border border-border bg-card rounded-xl shadow-xl">
            <div className="flex justify-center">
              <div className="p-3 bg-destructive/10 rounded-full">
                <AlertTriangle className="h-12 w-12 text-destructive" />
              </div>
            </div>
            <div className="space-y-2">
              <h1 className="text-xl font-bold">عذراً، حدث خطأ في النظام</h1>
              <p className="text-sm text-muted-foreground">
                حدثت مشكلة غير متوقعة أثناء تشغيل التطبيق. لقد تم تسجيل هذا الخطأ وسنقوم بإصلاحه قريباً.
              </p>
              {this.state.error && (
                <pre className="mt-4 p-3 bg-muted rounded text-left text-xs overflow-auto max-h-40 font-mono text-destructive">
                  {this.state.error.toString()}
                </pre>
              )}
            </div>
            <Button onClick={this.handleReset} className="w-full">
              العودة إلى الصفحة الرئيسية
            </Button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
