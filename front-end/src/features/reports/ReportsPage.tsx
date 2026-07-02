import { useState, useMemo, useEffect } from "react";
import { FileText, Send, Download, Lightbulb, Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import SectionCard from "@/components/SectionCard";
import { useChildren, useSessions, useParents, useDoctors } from "@/hooks/useApiData";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { generateRecommendations } from "@/lib/data-utils";
import { apiClient } from "@/lib/apiClient";
import { toast } from "sonner";

import { severityMapArabic, statusMapArabic } from '@/core/utils/translators';

const translateRecommendation = (rec: string): string => {
  if (rec.includes("No session data available")) return "لا تتوفر بيانات جلسات كافية لتوليد التوصيات.";
  if (rec.includes("Motor control below target")) return "التحكم الحركي أقل من المستهدف — يُنصح بتكثيف تمارين التوازن والثبات الحركي.";
  if (rec.includes("High impulsivity index")) return "مؤشر اندفاعية مرتفع — يُنصح بزيادة تمارين التوقف المفاجئ ومهام تأجيل الاستجابة لحفز كبح الاندفاع.";
  if (rec.includes("Elevated distraction score")) return "تشتت انتباه مرتفع — يُنصح بتقليل المشتتات البيئية المحيطة بالطفل أثناء الجلسات.";
  if (rec.includes("Slow reaction time")) return "سرعة الاستجابة بطيئة — يُنصح بإدخال أنشطة الاستجابة القائمة على الإيقاع والسرعة التدريجية.";
  if (rec.includes("Excessive false moves")) return "حركات خاطئة زائدة في المرحلة الحمراء — يُنصح بتعزيز إشارات المنع البصري والتغذية الراجعة الفورية.";
  if (rec.includes("Strong success rate")) return "معدل نجاح قوي وممتاز — يُنصح بالانتقال إلى مستوى الصعوبة التالي لتحدي قدرات الطفل.";
  if (rec.includes("Performance within target range")) return "الأداء ضمن النطاق المستهدف — يُنصح بمواصلة بروتوكول التدريب الحالي والحفاظ على الانتظام.";
  return rec;
};

export function ReportsPage() {
  const { children, loading: loadingChildren } = useChildren();
  const { parents, loading: loadingParents } = useParents();
  const { doctors, loading: loadingDoctors } = useDoctors();
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    if (children.length > 0 && !selectedId) {
      setSelectedId(children[0].id);
    }
  }, [children, selectedId]);

  const { sessions: allSessions, loading: loadingSessions } = useSessions(selectedId || undefined);

  const [email, setEmail] = useState("");
  const [dateFrom, setDateFrom] = useState(() => {
    const d = new Date();
    d.setMonth(d.getMonth() - 6);
    return d.toISOString().split("T")[0];
  });
  const [dateTo, setDateTo] = useState(() => new Date().toISOString().split("T")[0]);
  const [exported, setExported] = useState(false);
  const [sent, setSent] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [sending, setSending] = useState(false);
  const [sharingWhatsApp, setSharingWhatsApp] = useState(false);

  useEffect(() => {
    if (allSessions.length > 0) {
      const times = allSessions.map(s => new Date(s.sessionInfo.startTime).getTime());
      const maxTime = Math.max(...times);
      const minTime = Math.min(...times);

      const maxDateStr = new Date(maxTime).toISOString().split("T")[0];
      const sixMonthsAgo = new Date(maxTime);
      sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);
      const fromTime = Math.max(sixMonthsAgo.getTime(), minTime);
      const fromDateStr = new Date(fromTime).toISOString().split("T")[0];

      setDateFrom(fromDateStr);
      setDateTo(maxDateStr);
    }
  }, [allSessions]);

  const child = useMemo(() => children.find(c => c.id === selectedId), [children, selectedId]);

  const parent = useMemo(() => {
    if (!child || !child.parentId) return null;
    return parents.find(p => p.id === child.parentId);
  }, [parents, child]);

  const doctor = useMemo(() => {
    if (!child || !child.doctorId) return null;
    return doctors.find(d => d.id === child.doctorId);
  }, [doctors, child]);

  const doctorName = useMemo(() => {
    return doctor ? `د. ${doctor.userName}` : "د. سارة حسن";
  }, [doctor]);

  useEffect(() => {
    if (parent?.email) {
      setEmail(parent.email);
    } else {
      setEmail("");
    }
  }, [parent]);

  const filteredSessions = useMemo(() => {
    return allSessions.filter(s => {
      const d = new Date(s.sessionInfo.startTime);
      return d >= new Date(dateFrom) && d <= new Date(dateTo);
    });
  }, [allSessions, dateFrom, dateTo]);

  const recommendations = useMemo(() => generateRecommendations(filteredSessions), [filteredSessions]);

  const avgSuccess = filteredSessions.length
    ? filteredSessions.reduce((s, sess) => s + sess.summary.success_rate, 0) / filteredSessions.length
    : 0;
  const lastSession = filteredSessions[filteredSessions.length - 1];

  const handleExport = () => {
    if (!child) return;
    setExporting(true);

    try {
      const iframe = document.createElement("iframe");
      iframe.style.position = "absolute";
      iframe.style.width = "0px";
      iframe.style.height = "0px";
      iframe.style.border = "none";
      document.body.appendChild(iframe);

      const doc = iframe.contentWindow?.document || iframe.contentDocument;
      if (!doc) {
        throw new Error("Could not access iframe document");
      }

      const printHtml = `
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
          <meta charset="utf-8">
          <title>تقرير حالة الطفل - ${child.name}</title>
          <style>
            @media print {
              body {
                background: #ffffff;
                color: #0f172a;
                font-family: system-ui, -apple-system, sans-serif;
                margin: 20px;
                padding: 0;
              }
            }
            body {
              font-family: system-ui, -apple-system, sans-serif;
              color: #0f172a;
              direction: rtl;
              padding: 24px;
            }
            .header-container {
              border-bottom: 2px solid #e2e8f0;
              padding-bottom: 16px;
              margin-bottom: 24px;
              display: flex;
              justify-content: space-between;
              align-items: center;
            }
            .logo-title {
              font-size: 24px;
              font-weight: bold;
              color: #4f46e5;
            }
            .subtitle {
              font-size: 14px;
              color: #64748b;
              margin-top: 4px;
            }
            .section-title {
              font-size: 16px;
              font-weight: bold;
              color: #1e293b;
              margin-top: 24px;
              margin-bottom: 12px;
              border-bottom: 1px solid #cbd5e1;
              padding-bottom: 6px;
            }
            .info-grid {
              display: grid;
              grid-template-columns: repeat(2, 1fr);
              gap: 16px;
              background-color: #f8fafc;
              padding: 16px;
              border-radius: 8px;
              border: 1px solid #e2e8f0;
            }
            .info-item {
              font-size: 14px;
            }
            .info-label {
              color: #64748b;
              font-size: 12px;
              margin-bottom: 2px;
            }
            .info-value {
              font-weight: 600;
            }
            .sessions-stats {
              display: flex;
              justify-content: space-around;
              background-color: #eff6ff;
              border: 1px solid #bfdbfe;
              padding: 16px;
              border-radius: 8px;
              margin-top: 16px;
              text-align: center;
            }
            .stat-box {
              flex: 1;
            }
            .stat-value {
              font-size: 24px;
              font-weight: bold;
              color: #1e40af;
            }
            .stat-label {
              font-size: 12px;
              color: #1d4ed8;
              margin-top: 4px;
            }
            .metrics-grid {
              display: grid;
              grid-template-columns: repeat(5, 1fr);
              gap: 12px;
              margin-top: 12px;
            }
            .metric-card {
              border-radius: 8px;
              padding: 12px;
              text-align: center;
              font-size: 14px;
            }
            .metric-good {
              background-color: #f0fdf4;
              border: 1px solid #bbf7d0;
              color: #166534;
            }
            .metric-warn {
              background-color: #fffbeb;
              border: 1px solid #fef08a;
              color: #92400e;
            }
            .metric-card-val {
              font-size: 18px;
              font-weight: bold;
              margin-bottom: 4px;
            }
            .recommendation-card {
              background-color: #f5f3ff;
              border: 1px solid #ddd6fe;
              border-radius: 8px;
              padding: 12px;
              margin-bottom: 8px;
              font-size: 14px;
            }
            .footer {
              margin-top: 40px;
              text-align: center;
              font-size: 12px;
              color: #94a3b8;
              border-top: 1px solid #e2e8f0;
              padding-top: 16px;
            }
          </style>
        </head>
        <body>
          <div class="header-container">
            <div>
              <div class="logo-title">منصة ADHD Progress Insights - التقرير الطبي الدوري</div>
              <div class="subtitle">تقرير تحليل سلوك ومقاييس التركيز وتشتت الانتباه الدوري</div>
            </div>
            <div style="text-align: left; font-size: 12px; color: #64748b;">
              تاريخ الطباعة: ${new Date().toLocaleDateString("ar-EG")}
            </div>
          </div>

          <div class="section-title">ملخص معلومات الطفل</div>
          <div class="info-grid">
            <div class="info-item">
              <div class="info-label">اسم الطفل</div>
              <div class="info-value">${child.name}</div>
            </div>
            <div class="info-item">
              <div class="info-label">معرف الطفل (ID)</div>
              <div class="info-value">${child.id}</div>
            </div>
            <div class="info-item">
              <div class="info-label">العمر</div>
              <div class="info-value">${child.age} سنوات</div>
            </div>
            <div class="info-item">
              <div class="info-label">شدة الحالة</div>
              <div class="info-value">${severityMapArabic(child.diagnosisSeverity)}</div>
            </div>
            <div class="info-item">
              <div class="info-label">المعالج المشرف</div>
              <div class="info-value">${doctorName}</div>
            </div>
            <div class="info-item">
              <div class="info-label">حالة النشاط الحالية</div>
              <div class="info-value">${statusMapArabic(child.status)}</div>
            </div>
          </div>

          <div class="section-title">مؤشرات الفترة الزمنية (من ${dateFrom} إلى ${dateTo})</div>
          <div class="sessions-stats">
            <div class="stat-box">
              <div class="stat-value">${filteredSessions.length}</div>
              <div class="stat-label">إجمالي الجلسات المكتملة</div>
            </div>
            <div class="stat-box" style="border-right: 1px solid #bfdbfe;">
              <div class="stat-value">${avgSuccess.toFixed(1)}%</div>
              <div class="stat-label">متوسط نسبة النجاح</div>
            </div>
          </div>

          ${lastSession
          ? `
            <div class="section-title">مؤشرات الجلسة الأخيرة المكتملة</div>
            <div class="metrics-grid">
              <div class="metric-card ${lastSession.summary.success_rate >= 80 ? "metric-good" : "metric-warn"}">
                <div class="metric-card-val">${lastSession.summary.success_rate.toFixed(1)}%</div>
                <div>معدل النجاح</div>
              </div>
              <div class="metric-card ${lastSession.summary.motor_control_score >= 75 ? "metric-good" : "metric-warn"}">
                <div class="metric-card-val">${lastSession.summary.motor_control_score.toFixed(1)}</div>
                <div>التحكم الحركي</div>
              </div>
              <div class="metric-card ${lastSession.summary.impulsivity_index <= 15 ? "metric-good" : "metric-warn"}">
                <div class="metric-card-val">${lastSession.summary.impulsivity_index.toFixed(1)}</div>
                <div>مؤشر الاندفاعية</div>
              </div>
              <div class="metric-card ${lastSession.summary.distraction_score <= 15 ? "metric-good" : "metric-warn"}">
                <div class="metric-card-val">${lastSession.summary.distraction_score.toFixed(1)}</div>
                <div>مؤشر التشتت</div>
              </div>
              <div class="metric-card ${lastSession.summary.avg_reaction_time <= 0.45 ? "metric-good" : "metric-warn"}">
                <div class="metric-card-val">${(lastSession.summary.avg_reaction_time * 1000).toFixed(0)} ms</div>
                <div>زمن الاستجابة</div>
              </div>
            </div>
          `
          : ""
        }

          <div class="section-title">التوصيات الطبية المقترحة بالذكاء الاصطناعي</div>
          <div>
            ${recommendations
          .map(
            (rec, i) => `
              <div class="recommendation-card">
                <strong>توصية #${i + 1}:</strong> ${translateRecommendation(rec)}
              </div>
            `
          )
          .join("")}
          </div>

          <div class="footer">
            <p>تم توليد هذا التقرير وتصديره تلقائياً عبر منصة ADHD Progress Insights.</p>
            <p>© 2026 منصة ADHD Progress Insights. جميع الحقوق محفوظة.</p>
          </div>
        </body>
        </html>
      `;

      doc.open();
      doc.write(printHtml);
      doc.close();

      setTimeout(() => {
        iframe.contentWindow?.focus();
        iframe.contentWindow?.print();
        setTimeout(() => {
          document.body.removeChild(iframe);
        }, 1000);

        setExported(true);
        toast.success("تم تجهيز التقرير وتصديره بنجاح");
        setTimeout(() => setExported(false), 3000);
        setExporting(false);
      }, 500);

    } catch (error: any) {
      console.error(error);
      toast.error("فشل تصدير التقرير الطبي");
      setExporting(false);
    }
  };

  const handleSend = async () => {
    if (!email) {
      toast.error("يرجى إدخال البريد الإلكتروني");
      return;
    }
    if (!child) return;

    setSending(true);
    try {
      const payload = {
        email,
        childId: child.id,
        childName: child.name,
        age: child.age,
        severity: severityMapArabic(child.diagnosisSeverity),
        doctorName: doctorName,
        dateFrom,
        dateTo,
        sessionCount: filteredSessions.length,
        avgSuccess,
        status: statusMapArabic(child.status),
        lastSuccessRate: lastSession?.summary.success_rate || null,
        lastMotorControl: lastSession?.summary.motor_control_score || null,
        lastImpulsivity: lastSession?.summary.impulsivity_index || null,
        lastDistraction: lastSession?.summary.distraction_score || null,
        lastReactionTime: lastSession?.summary.avg_reaction_time || null,
        recommendations: recommendations.map(rec => translateRecommendation(rec))
      };

      await apiClient.post("reports/send-email", payload);

      setSent(true);
      toast.success("تم إرسال التقرير الطبي إلى البريد الإلكتروني بنجاح");
      setTimeout(() => setSent(false), 3000);
    } catch (error: any) {
      console.error(error);
      toast.error(error.message || "حدث خطأ أثناء إرسال البريد الإلكتروني");
    } finally {
      setSending(false);
    }
  };

  const handleShareWhatsApp = async () => {
    if (!child) return;
    setSharingWhatsApp(true);
    try {
      const payload = {
        childId: child.id,
        childName: child.name,
        age: child.age,
        severity: severityMapArabic(child.diagnosisSeverity),
        doctorName: doctorName,
        dateFrom,
        dateTo,
        sessionCount: filteredSessions.length,
        avgSuccess,
        status: statusMapArabic(child.status),
        lastSuccessRate: lastSession?.summary.success_rate || null,
        lastMotorControl: lastSession?.summary.motor_control_score || null,
        lastImpulsivity: lastSession?.summary.impulsivity_index || null,
        lastDistraction: lastSession?.summary.distraction_score || null,
        lastReactionTime: lastSession?.summary.avg_reaction_time || null,
        recommendations: recommendations.map(rec => translateRecommendation(rec))
      };

      const response: any = await apiClient.post("reports/send-whatsapp", payload);

      if (response && response.succeeded && response.data) {
        const url = /Android|iPhone|iPad/i.test(navigator.userAgent)
          ? response.data.mobileUrl
          : response.data.webUrl;

        window.open(url, "_blank");
        toast.success("تم توليد رسالة المشاركة وفتح الواتساب بنجاح");
      }
    } catch (error: any) {
      console.error(error);
      toast.error("فشل مشاركة التقرير عبر الواتساب");
    } finally {
      setSharingWhatsApp(false);
    }
  };

  if (loadingChildren || loadingParents || loadingDoctors || (selectedId && loadingSessions)) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-[200px] w-full rounded-xl" />
        <Skeleton className="h-[400px] w-full rounded-xl" />
      </div>
    );
  }

  return (
    <div className="space-y-6 text-right animate-fade-in" dir="rtl">
      {/* Controls */}
      <SectionCard title="إعداد التقرير الطبي" subtitle="اختر الطفل والفترة الزمنية لتوليد التقرير">
        <div className="flex flex-wrap gap-4 items-end justify-start">
          <div className="flex flex-col gap-1.5 text-right">
            <label className="text-xs font-medium text-muted-foreground">الطفل المريض</label>
            <Select value={selectedId || ""} onValueChange={setSelectedId}>
              <SelectTrigger className="w-56 text-right">
                <SelectValue placeholder="اختر الطفل المريض..." />
              </SelectTrigger>
              <SelectContent>
                {children.map(c => (
                  <SelectItem key={c.id} value={c.id} className="text-right">{c.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex flex-col gap-1.5 text-right">
            <label className="text-xs font-medium text-muted-foreground">من تاريخ</label>
            <Input type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)} className="w-40 text-right" />
          </div>
          <div className="flex flex-col gap-1.5 text-right">
            <label className="text-xs font-medium text-muted-foreground">إلى تاريخ</label>
            <Input type="date" value={dateTo} onChange={e => setDateTo(e.target.value)} className="w-40 text-right" />
          </div>
          <Badge variant="secondary" className="h-9 px-3 flex items-center gap-1.5 mr-auto sm:mr-0 ml-0 sm:ml-auto">
            <Calendar size={14} />
            {filteredSessions.length} جلسة في هذه الفترة
          </Badge>
        </div>
      </SectionCard>

      {/* Report Preview */}
      {child && (
        <SectionCard
          title="معاينة التقرير"
          subtitle={`${child.name} · من ${dateFrom} إلى ${dateTo}`}
          action={
            <div className="flex gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={handleExport}
                disabled={exporting}
                className={cn(exported && "border-success text-success")}
              >
                <Download size={14} className={cn("ml-1.5", exporting && "animate-spin")} />
                {exporting ? "جاري التوليد..." : exported ? "تم التصدير!" : "تصدير PDF"}
              </Button>
            </div>
          }
        >
          <div className="space-y-6 text-right">
            {/* Patient info */}
            <div className="flex flex-col md:flex-row items-center md:items-start gap-4 p-4 rounded-xl border border-border bg-muted/30">
              <div className="w-12 h-12 rounded-full gradient-primary flex items-center justify-center flex-shrink-0">
                <span className="text-base font-bold text-primary-foreground">{child.avatarInitials}</span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 flex-1 text-sm text-right w-full">
                <div><p className="text-xs text-muted-foreground">معرف الطفل</p><p className="font-semibold">{child.id}</p></div>
                <div><p className="text-xs text-muted-foreground">الاسم</p><p className="font-semibold">{child.name}</p></div>
                <div><p className="text-xs text-muted-foreground">العمر</p><p className="font-semibold">{child.age} سنوات</p></div>
                <div><p className="text-xs text-muted-foreground">شدة الحالة</p><p className="font-semibold capitalize">{severityMapArabic(child.diagnosisSeverity)}</p></div>
                <div><p className="text-xs text-muted-foreground">المعالج المشرف</p><p className="font-semibold">{doctorName}</p></div>
                <div><p className="text-xs text-muted-foreground">عدد الجلسات</p><p className="font-semibold">{filteredSessions.length}</p></div>
                <div><p className="text-xs text-muted-foreground">متوسط النجاح</p><p className="font-semibold text-primary">{avgSuccess.toFixed(1)}%</p></div>
                <div><p className="text-xs text-muted-foreground">حالة النشاط</p><p className="font-semibold capitalize">{statusMapArabic(child.status)}</p></div>
              </div>
            </div>

            {/* Last Session */}
            {lastSession && (
              <div>
                <h4 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2 justify-end">
                  <span>مؤشرات الجلسة الأخيرة</span>
                  <FileText size={14} className="text-primary" />
                </h4>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
                  {[
                    { label: "معدل النجاح", value: `${lastSession.summary.success_rate.toFixed(1)}%`, good: lastSession.summary.success_rate >= 80 },
                    { label: "التحكم الحركي", value: lastSession.summary.motor_control_score.toFixed(1), good: lastSession.summary.motor_control_score >= 75 },
                    { label: "مؤشر الاندفاعية", value: lastSession.summary.impulsivity_index.toFixed(1), good: lastSession.summary.impulsivity_index <= 15 },
                    { label: "مؤشر التشتت", value: lastSession.summary.distraction_score.toFixed(1), good: lastSession.summary.distraction_score <= 15 },
                    { label: "زمن الاستجابة", value: `${(lastSession.summary.avg_reaction_time * 1000).toFixed(0)} ملي ثانية`, good: lastSession.summary.avg_reaction_time <= 0.45 },
                  ].map(({ label, value, good }) => (
                    <div key={label} className={cn("rounded-lg p-3 text-center", good ? "status-success" : "status-warning")}>
                      <p className="text-lg font-bold">{value}</p>
                      <p className="text-xs opacity-80">{label}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendations */}
            <div>
              <h4 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2 justify-end">
                <span>التوصيات التلقائية المقترحة (الذكاء الاصطناعي)</span>
                <Lightbulb size={14} className="text-accent" />
              </h4>
              <div className="space-y-2">
                {recommendations.map((rec, i) => (
                  <div key={i} className="flex items-start justify-between gap-3 p-3 rounded-lg bg-accent/10 border border-accent/20 text-right">
                    <p className="text-sm text-foreground flex-1">{translateRecommendation(rec)}</p>
                    <span className="text-accent font-bold text-xs mt-0.5 flex-shrink-0">#{i + 1}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </SectionCard>
      )}

      {/* Share & Send Section */}
      <SectionCard title="إرسال ومشاركة التقرير الطبي" subtitle="شارك التقرير الطبي الدوري مباشرة مع ولي الأمر أو الفريق الطبي">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-right">

          {/* Email Form */}
          <div className="space-y-3 p-4 rounded-xl border border-border bg-card/50">
            <h4 className="text-sm font-semibold text-foreground flex items-center gap-2 justify-end">
              <span>إرسال بالبريد الإلكتروني</span>
              <Send size={16} className="text-primary" />
            </h4>
            <p className="text-xs text-muted-foreground leading-relaxed text-right">
              سيتم إرسال نسخة منسقة بالكامل بصيغة HTML للتقرير الطبي إلى عنوان البريد الإلكتروني المدخل مباشرة عبر سيرفر المنصة.
            </p>
            <div className="flex gap-2">
              <Input
                type="email"
                placeholder="name@example.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="flex-1 text-right border-border bg-background focus-visible:ring-indigo-500"
              />
              <Button
                onClick={handleSend}
                disabled={!email || sending}
                className={cn("gradient-primary text-primary-foreground border-0", sent && "bg-success gradient-success")}
              >
                <Send size={14} className={cn("ml-1.5", sending && "animate-spin")} />
                {sending ? "جاري الإرسال..." : sent ? "تم الإرسال!" : "إرسال"}
              </Button>
            </div>
            {sent && <p className="text-xs text-success text-right">✓ تم إرسال البريد بنجاح إلى {email}</p>}
          </div>

          {/* WhatsApp Share */}
          <div className="space-y-3 p-4 rounded-xl border border-border bg-card/50">
            <h4 className="text-sm font-semibold text-foreground flex items-center gap-2 justify-end">
              <span>مشاركة عبر الواتساب (WhatsApp)</span>
              <svg className="w-4 h-4 text-emerald-500 fill-current" viewBox="0 0 24 24">
                <path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946C.06 5.348 5.397.01 12.008.01c3.202.001 6.212 1.246 8.477 3.513 2.262 2.268 3.507 5.28 3.505 8.484-.004 6.657-5.34 11.997-11.953 11.997-2.005-.001-3.973-.502-5.717-1.456L0 24zm6.59-4.846c1.6.95 3.188 1.449 4.825 1.451 5.436 0 9.86-4.37 9.864-9.799.002-2.63-1.023-5.101-2.885-6.97C16.528 2.017 14.077.99 11.502.99c-5.437 0-9.862 4.37-9.866 9.8.001 1.954.513 3.86 1.482 5.545l-1.002 3.653 3.753-.984z" />
              </svg>
            </h4>
            <p className="text-xs text-muted-foreground leading-relaxed text-right">
              شارك ملخص مؤشرات أداء الطفل الحالي وأبرز توصيات الذكاء الاصطناعي ونتائج الجلسات مباشرة عبر الواتساب مع ولي الأمر.
            </p>
            <Button
              onClick={handleShareWhatsApp}
              disabled={sharingWhatsApp}
              className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-medium flex items-center justify-center gap-2 shadow-md shadow-emerald-100/50"
            >
              <svg className="w-4 h-4 fill-current ml-1" viewBox="0 0 24 24">
                <path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946C.06 5.348 5.397.01 12.008.01c3.202.001 6.212 1.246 8.477 3.513 2.262 2.268 3.507 5.28 3.505 8.484-.004 6.657-5.34 11.997-11.953 11.997-2.005-.001-3.973-.502-5.717-1.456L0 24zm6.59-4.846c1.6.95 3.188 1.449 4.825 1.451 5.436 0 9.86-4.37 9.864-9.799.002-2.63-1.023-5.101-2.885-6.97C16.528 2.017 14.077.99 11.502.99c-5.437 0-9.862 4.37-9.866 9.8.001 1.954.513 3.86 1.482 5.545l-1.002 3.653 3.753-.984z" />
              </svg>
              {sharingWhatsApp ? "جاري تجهيز الرابط..." : "مشاركة التقرير عبر الواتساب"}
            </Button>
          </div>

        </div>
      </SectionCard>
    </div>
  );
}

export default ReportsPage;
