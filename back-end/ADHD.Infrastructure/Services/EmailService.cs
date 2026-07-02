using ADHD.Application.Interfaces;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using System;
using System.IO;
using System.Net;
using System.Net.Mail;
using System.Threading.Tasks;

namespace ADHD.Infrastructure.Services
{
    public class EmailService : IEmailService
    {
        private readonly IConfiguration _configuration;
        private readonly ILogger<EmailService> _logger;

        public EmailService(IConfiguration configuration, ILogger<EmailService> logger)
        {
            _configuration = configuration;
            _logger = logger;
        }

        public async Task SendEmailAsync(string toEmail, string subject, string htmlMessage)
        {
            var host = _configuration["Smtp:Host"];
            var portStr = _configuration["Smtp:Port"];
            var enableSslStr = _configuration["Smtp:EnableSsl"];
            var username = _configuration["Smtp:Username"];
            var password = _configuration["Smtp:Password"];
            var fromEmail = _configuration["Smtp:FromEmail"] ?? "no-reply@ehtwaa.com";
            var fromName = _configuration["Smtp:FromName"] ?? "Ehtwaa Platform";

            // If SMTP is not configured or uses default placeholders, fallback to local file simulation
            if (string.IsNullOrEmpty(host) || string.IsNullOrEmpty(username) || username.Contains("placeholder") || password == "your-app-password")
            {
                await SimulateEmailSendingAsync(toEmail, subject, htmlMessage);
                return;
            }

            try
            {
                int port = int.TryParse(portStr, out var p) ? p : 587;
                bool enableSsl = !bool.TryParse(enableSslStr, out var ssl) || ssl;

                using (var client = new SmtpClient(host, port))
                {
                    client.UseDefaultCredentials = false;
                    client.Credentials = new NetworkCredential(username, password);
                    client.EnableSsl = enableSsl;

                    var mailMessage = new MailMessage
                    {
                        From = new MailAddress(fromEmail, fromName),
                        Subject = subject,
                        Body = htmlMessage,
                        IsBodyHtml = true
                    };
                    mailMessage.To.Add(toEmail);

                    await client.SendMailAsync(mailMessage);
                    _logger.LogInformation("Email sent successfully to {ToEmail}", toEmail);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to send email to {ToEmail} via SMTP. Falling back to simulation.", toEmail);
                await SimulateEmailSendingAsync(toEmail, subject, htmlMessage);
            }
        }

        private async Task SimulateEmailSendingAsync(string toEmail, string subject, string htmlMessage)
        {
            try
            {
                var directoryPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "temp_emails");
                if (!Directory.Exists(directoryPath))
                {
                    Directory.CreateDirectory(directoryPath);
                }

                var fileName = $"Email_{DateTime.UtcNow:yyyyMMdd_HHmmss}_{Guid.NewGuid().ToString().Substring(0, 8)}.html";
                var filePath = Path.Combine(directoryPath, fileName);

                var logContent = $"<!-- TO: {toEmail} -->\n<!-- SUBJECT: {subject} -->\n\n{htmlMessage}";
                await File.WriteAllTextAsync(filePath, logContent);

                _logger.LogWarning("SMTP not configured or failed. Simulated email saved locally to: {FilePath}", filePath);
                Console.WriteLine($"\n[EMAIL SIMULATION] Sent to: {toEmail} | Subject: {subject} | Saved to: {filePath}\n");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to write simulated email to disk.");
            }
        }
    }
}
