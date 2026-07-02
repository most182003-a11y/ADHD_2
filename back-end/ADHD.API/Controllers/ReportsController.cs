using ADHD.Application.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;

namespace ADHD.API.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    [Authorize(Roles = "Admin,Doctor")]
    public class ReportsController : ControllerBase
    {
        private readonly IEmailService _emailService;

        public ReportsController(IEmailService emailService)
        {
            _emailService = emailService;
        }

        public class SendReportRequest
        {
            public string? Email { get; set; } = string.Empty;
            public string ChildId { get; set; } = string.Empty;
            public string ChildName { get; set; } = string.Empty;
            public int Age { get; set; }
            public string Severity { get; set; } = string.Empty;
            public string DoctorName { get; set; } = string.Empty;
            public string DateFrom { get; set; } = string.Empty;
            public string DateTo { get; set; } = string.Empty;
            public int SessionCount { get; set; }
            public double AvgSuccess { get; set; }
            public string Status { get; set; } = string.Empty;

            // Last session metrics
            public double? LastSuccessRate { get; set; }
            public double? LastMotorControl { get; set; }
            public double? LastImpulsivity { get; set; }
            public double? LastDistraction { get; set; }
            public double? LastReactionTime { get; set; }

            public List<string> Recommendations { get; set; } = new List<string>();
        }

        [HttpPost("send-email")]
        public async Task<IActionResult> SendReportEmail([FromBody] SendReportRequest request)
        {
            if (string.IsNullOrEmpty(request.Email))
            {
                return BadRequest(new { succeeded = false, message = "البريد الإلكتروني مطلوب" });
            }

            try
            {
                var htmlContent = GenerateArabicReportHtml(request);
                var subject = $"تقرير طبي لمتابعة حالة الطفل: {request.ChildName}";

                await _emailService.SendEmailAsync(request.Email, subject, htmlContent);

                return Ok(new
                {
                    succeeded = true,
                    message = "تم إرسال التقرير الطبي بالبريد الإلكتروني بنجاح"
                });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new
                {
                    succeeded = false,
                    message = $"حدث خطأ أثناء إرسال البريد: {ex.Message}"
                });
            }
        }

        [HttpPost("send-whatsapp")]
        public IActionResult SendReportWhatsApp([FromBody] SendReportRequest request)
        {
            // WhatsApp Business API calls are simulated here.
            // In a real production environment, you would use Twilio or WhatsApp Cloud API.
            // We return a simulated success status along with a pre-filled wa.me redirect link for immediate developer/user use!
            
            var messageText = $"*تقرير طبي لمتابعة حالة الطفل*: {request.ChildName}\n" +
                              $"*العمر*: {request.Age} سنوات\n" +
                              $"*الفترة*: من {request.DateFrom} إلى {request.DateTo}\n" +
                              $"*عدد الجلسات*: {request.SessionCount}\n" +
                              $"*متوسط نسبة النجاح*: {request.AvgSuccess:F1}%\n" +
                              $"*حالة النشاط*: {request.Status}\n" +
                              $"*المعالج المشرف*: {request.DoctorName}\n\n" +
                              $"_تم توليد هذا التقرير تلقائياً بواسطة منصة ADHD Progress Insights_";

            var encodedText = Uri.EscapeDataString(messageText);
            var whatsappWebUrl = $"https://web.whatsapp.com/send?text={encodedText}";
            var whatsappMobileUrl = $"https://wa.me/?text={encodedText}";

            Console.WriteLine($"\n[WHATSAPP SIMULATION] Message generated for Child: {request.ChildName}!\n{messageText}\n");

            return Ok(new
            {
                succeeded = true,
                message = "تم محاكاة إرسال التقرير عبر الواتساب وتوليد رابط الإرسال المباشر",
                data = new
                {
                    mobileUrl = whatsappMobileUrl,
                    webUrl = whatsappWebUrl,
                    messageText = messageText
                }
            });
        }

        private string GenerateArabicReportHtml(SendReportRequest request)
        {
            var recsBuilder = new StringBuilder();
            if (request.Recommendations != null && request.Recommendations.Count > 0)
            {
                int index = 1;
                foreach (var rec in request.Recommendations)
                {
                    recsBuilder.Append($@"
                        <div style='background-color: #f5f3ff; border: 1px solid #ddd6fe; padding: 12px; border-radius: 8px; margin-bottom: 8px; display: flex; align-items: start; gap: 10px;'>
                            <span style='color: #6d28d9; font-weight: bold; margin-left: 8px;'>#{index++}</span>
                            <p style='margin: 0; font-size: 14px; color: #1f2937; text-align: right;'>{rec}</p>
                        </div>");
                }
            }
            else
            {
                recsBuilder.Append("<p style='color: #6b7280; font-size: 14px; text-align: center;'>لا توجد توصيات متوفرة لهذه الفترة.</p>");
            }

            var lastSessionHtml = "";
            if (request.LastSuccessRate.HasValue)
            {
                lastSessionHtml = $@"
                    <div style='margin-top: 25px;'>
                        <h4 style='color: #4b5563; font-size: 15px; margin-bottom: 12px; border-bottom: 1px solid #e5e7eb; padding-bottom: 5px;'>📊 مؤشرات الجلسة الأخيرة المكتملة</h4>
                        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 10px; margin-top: 10px;'>
                            <div style='background-color: #ecfdf5; border: 1px solid #a7f3d0; padding: 10px; border-radius: 8px; text-align: center;'>
                                <p style='font-size: 18px; font-weight: bold; color: #065f46; margin: 0;'>{request.LastSuccessRate:F1}%</p>
                                <p style='font-size: 11px; color: #047857; margin: 2px 0 0 0;'>معدل النجاح</p>
                            </div>
                            <div style='background-color: #fef3c7; border: 1px solid #fde68a; padding: 10px; border-radius: 8px; text-align: center;'>
                                <p style='font-size: 18px; font-weight: bold; color: #92400e; margin: 0;'>{request.LastMotorControl:F1}</p>
                                <p style='font-size: 11px; color: #b45309; margin: 2px 0 0 0;'>التحكم الحركي</p>
                            </div>
                            <div style='background-color: #fee2e2; border: 1px solid #fecaca; padding: 10px; border-radius: 8px; text-align: center;'>
                                <p style='font-size: 18px; font-weight: bold; color: #991b1b; margin: 0;'>{request.LastImpulsivity:F1}</p>
                                <p style='font-size: 11px; color: #b91c1c; margin: 2px 0 0 0;'>الاندفاعية</p>
                            </div>
                            <div style='background-color: #eff6ff; border: 1px solid #bfdbfe; padding: 10px; border-radius: 8px; text-align: center;'>
                                <p style='font-size: 18px; font-weight: bold; color: #1e3a8a; margin: 0;'>{request.LastDistraction:F1}</p>
                                <p style='font-size: 11px; color: #1d4ed8; margin: 2px 0 0 0;'>مؤشر التشتت</p>
                            </div>
                            <div style='background-color: #f3f4f6; border: 1px solid #e5e7eb; padding: 10px; border-radius: 8px; text-align: center;'>
                                <p style='font-size: 18px; font-weight: bold; color: #374151; margin: 0;'>{(request.LastReactionTime * 1000):F0} ms</p>
                                <p style='font-size: 11px; color: #4b5563; margin: 2px 0 0 0;'>سرعة الاستجابة</p>
                            </div>
                        </div>
                    </div>";
            }

            return $@"
            <!DOCTYPE html>
            <html dir='rtl' lang='ar'>
            <head>
                <meta charset='utf-8'>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background-color: #f3f4f6;
                        margin: 0;
                        padding: 20px;
                        color: #1f2937;
                    }}
                    .container {{
                        max-width: 650px;
                        background-color: #ffffff;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                        border: 1px solid #e5e7eb;
                        margin: 0 auto;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                        padding: 30px 20px;
                        text-align: center;
                        color: #ffffff;
                    }}
                    .content {{
                        padding: 25px;
                    }}
                    .footer {{
                        background-color: #f9fafb;
                        padding: 15px 20px;
                        text-align: center;
                        font-size: 12px;
                        color: #6b7280;
                        border-top: 1px solid #e5e7eb;
                    }}
                    .grid {{
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 15px;
                        background-color: #f9fafb;
                        padding: 15px;
                        border-radius: 10px;
                        border: 1px solid #f3f4f6;
                        margin-top: 15px;
                    }}
                    .metric-label {{
                        color: #6b7280;
                        font-size: 12px;
                        margin-bottom: 2px;
                    }}
                    .metric-value {{
                        font-weight: bold;
                        font-size: 14px;
                        color: #111827;
                    }}
                </style>
            </head>
            <body>
                <div class='container'>
                    <div class='header'>
                        <h2 style='margin: 0; font-size: 22px;'>منصة ADHD Progress Insights - التقرير الطبي الدوري</h2>
                        <p style='margin: 5px 0 0 0; opacity: 0.9; font-size: 13px;'>تقرير متابعة الجلسات التدريبية والتحليلات الطبية</p>
                    </div>
                    <div class='content'>
                        <h3 style='color: #4f46e5; margin-top: 0; font-size: 18px; border-bottom: 2px solid #f3f4f6; padding-bottom: 8px;'>📋 ملخص بيانات الحالة</h3>
                        
                        <div class='grid'>
                            <div>
                                <div class='metric-label'>اسم الطفل المريض</div>
                                <div class='metric-value'>{request.ChildName}</div>
                            </div>
                            <div>
                                <div class='metric-label'>معرف الطفل (ID)</div>
                                <div class='metric-value'>{request.ChildId}</div>
                            </div>
                            <div>
                                <div class='metric-label'>العمر</div>
                                <div class='metric-value'>{request.Age} سنوات</div>
                            </div>
                            <div>
                                <div class='metric-label'>شدة الحالة التشخيصية</div>
                                <div class='metric-value'>{request.Severity}</div>
                            </div>
                            <div>
                                <div class='metric-label'>المعالج المشرف</div>
                                <div class='metric-value'>{request.DoctorName}</div>
                            </div>
                            <div>
                                <div class='metric-label'>حالة النشاط</div>
                                <div class='metric-value'>{request.Status}</div>
                            </div>
                        </div>

                        <div style='margin-top: 25px;'>
                            <h4 style='color: #4b5563; font-size: 15px; margin-bottom: 8px; border-bottom: 1px solid #e5e7eb; padding-bottom: 5px;'>📈 نتائج الفترة الزمنية (من {request.DateFrom} إلى {request.DateTo})</h4>
                            <div style='display: flex; justify-content: space-around; background-color: #eff6ff; border: 1px solid #dbeafe; padding: 15px; border-radius: 8px;'>
                                <div style='text-align: center;'>
                                    <span style='font-size: 24px; font-weight: bold; color: #1e40af;'>{request.SessionCount}</span>
                                    <p style='margin: 2px 0 0 0; font-size: 12px; color: #1e40af;'>إجمالي الجلسات</p>
                                </div>
                                <div style='text-align: center; border-right: 1px solid #bfdbfe; padding-right: 25px;'>
                                    <span style='font-size: 24px; font-weight: bold; color: #1e40af;'>{request.AvgSuccess:F1}%</span>
                                    <p style='margin: 2px 0 0 0; font-size: 12px; color: #1e40af;'>متوسط النجاح</p>
                                </div>
                            </div>
                        </div>

                        {lastSessionHtml}

                        <div style='margin-top: 25px;'>
                            <h4 style='color: #4b5563; font-size: 15px; margin-bottom: 12px; border-bottom: 1px solid #e5e7eb; padding-bottom: 5px;'>💡 توصيات الذكاء الاصطناعي المقترحة</h4>
                            {recsBuilder}
                        </div>
                    </div>
                    <div class='content' style='background-color: #faf5ff; border-top: 1px dashed #e9d5ff; padding: 15px; text-align: center;'>
                        <p style='margin: 0; font-size: 12px; color: #6b21a8;'>💡 يُنصح بمواصلة التدريب والالتزام بعدد الجلسات الأسبوعي الموصى به لتحقيق أفضل تحسن حركي وذهني للطفل.</p>
                    </div>
                    <div class='footer'>
                        <p style='margin: 0;'>هذا البريد تم توليده تلقائياً بواسطة منصة ADHD Progress Insights.</p>
                        <p style='margin: 5px 0 0 0; font-size: 10px; color: #9ca3af;'>© 2026 منصة ADHD Progress Insights. جميع الحقوق محفوظة.</p>
                    </div>
                </div>
            </body>
            </html>";
        }
    }
}
