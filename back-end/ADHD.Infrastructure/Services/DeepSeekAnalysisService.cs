using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using ADHD.Application.Interfaces;
using Microsoft.Extensions.Configuration;

namespace ADHD.Infrastructure.Services
{
    public class DeepSeekAnalysisService : IAnalysisService
    {
        private readonly HttpClient _httpClient;
        private readonly string _apiKey;
        private readonly string _apiUrl;
        private readonly string _model;

        public DeepSeekAnalysisService(HttpClient httpClient, IConfiguration configuration)
        {
            _httpClient = httpClient;

            _apiKey = Environment.GetEnvironmentVariable("DEEPSEEK_API_KEY")
                      ?? configuration["DeepSeek:ApiKey"]
                      ?? string.Empty;

            _apiUrl = configuration["DeepSeek:ApiUrl"] ?? "https://api.deepseek.com/v1/chat/completions";
            _model = configuration["DeepSeek:Model"] ?? "deepseek-chat";
        }

        public async Task<AnalysisResult> AnalyzeSessionAsync(
            string childId, string sessionId, int previousSessionsCount,
            object sessionData, object[]? trials, object summary)
        {
            try
            {
                var requestPayload = new
                {
                    userId = childId,
                    sessionId = sessionId,
                    gameType = "Imitation",
                    timestamp = DateTime.UtcNow.ToString("o"),
                    previousSessionsCount = previousSessionsCount,
                    trials = trials ?? Array.Empty<object>(),
                    sessionSummary = summary
                };

                var rawRequestJson = JsonSerializer.Serialize(requestPayload, new JsonSerializerOptions
                {
                    WriteIndented = true
                });

                var systemPrompt = @"أنت محلل أداء أطفال ADHD متخصص. دورك هو تحليل بيانات جلسة تدريب لطفل مصاب باضطراب فرط الحركة وتشتت الانتباه.

حلل البيانات التالية بدقة وأرجع JSON بالشكل التالي فقط (بدون markdown أو شرح إضافي):
{
  ""scores"": {
    ""attention"": 0-100,
    ""impulsivity"": 0-100,
    ""motorControl"": 0-100
  },
  ""trend"": {
    ""attentionChange"": ""+X%"",
    ""impulsivityChange"": ""-X%"",
    ""motorControlChange"": ""+X%""
  },
  ""summaryText"": ""نص ملخص بالعربية عن أداء الطفل في هذه الجلسة"",
  ""recommendations"": [
    ""توصية 1"",
    ""توصية 2"",
    ""توصية 3""
  ]
}

تعليمات هامة:
- attention: كلما زاد كلما كان أفضل (مدى الانتباه والتركيز)
- impulsivity: كلما قل كلما كان أفضل (التحكم في الاندفاع)
- motorControl: كلما زاد كلما كان أفضل (التحكم الحركي)
- trend: يقارن أداء هذه الجلسة بمتوسط أداء الجلسات السابقة (إذا كان previousSessionsCount = 0 اجعل التغيير 0%)
- summaryText: باللغة العربية الفصحى، موجز ومفيد
- recommendations: من 2 إلى 4 توصيات مخصصة بناءً على أداء الطفل";

                var requestBody = new
                {
                    model = _model,
                    messages = new[]
                    {
                        new { role = "system", content = systemPrompt },
                        new { role = "user", content = rawRequestJson }
                    },
                    temperature = 0.3,
                    max_tokens = 2000
                };

                var httpContent = new StringContent(
                    JsonSerializer.Serialize(requestBody),
                    Encoding.UTF8,
                    "application/json");

                if (!string.IsNullOrEmpty(_apiKey))
                {
                    _httpClient.DefaultRequestHeaders.Remove("Authorization");
                    _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {_apiKey}");
                }

                var response = await _httpClient.PostAsync(_apiUrl, httpContent);
                var responseBody = await response.Content.ReadAsStringAsync();

                if (!response.IsSuccessStatusCode)
                {
                    return new AnalysisResult
                    {
                        IsSuccessful = false,
                        ErrorMessage = $"API call failed: {response.StatusCode} - {responseBody}",
                        RawRequestJson = rawRequestJson,
                        RawResponseJson = responseBody,
                        ModelUsed = _model
                    };
                }

                var rawResponseJson = responseBody;

                using var jsonDoc = JsonDocument.Parse(responseBody);
                var root = jsonDoc.RootElement;

                var content = root.GetProperty("choices")[0].GetProperty("message").GetProperty("content").GetString();

                if (string.IsNullOrEmpty(content))
                {
                    return new AnalysisResult
                    {
                        IsSuccessful = false,
                        ErrorMessage = "Empty response from LLM",
                        RawRequestJson = rawRequestJson,
                        RawResponseJson = rawResponseJson,
                        ModelUsed = _model
                    };
                }

                content = content.Trim();
                if (content.StartsWith("```json")) content = content.Substring(7);
                if (content.StartsWith("```")) content = content.Substring(3);
                if (content.EndsWith("```")) content = content.Substring(0, content.Length - 3);
                content = content.Trim();

                using var resultDoc = JsonDocument.Parse(content);
                var resultRoot = resultDoc.RootElement;

                var scores = resultRoot.GetProperty("scores");
                var trend = resultRoot.GetProperty("trend");

                var result = new AnalysisResult
                {
                    AttentionScore = scores.GetProperty("attention").GetDouble(),
                    ImpulsivityScore = scores.GetProperty("impulsivity").GetDouble(),
                    MotorControlScore = scores.GetProperty("motorControl").GetDouble(),
                    AttentionChange = trend.GetProperty("attentionChange").GetString(),
                    ImpulsivityChange = trend.GetProperty("impulsivityChange").GetString(),
                    MotorControlChange = trend.GetProperty("motorControlChange").GetString(),
                    SummaryText = resultRoot.GetProperty("summaryText").GetString(),
                    Recommendations = JsonSerializer.Deserialize<string[]>(
                        resultRoot.GetProperty("recommendations").GetRawText()),
                    IsSuccessful = true,
                    RawRequestJson = rawRequestJson,
                    RawResponseJson = rawResponseJson,
                    ModelUsed = _model
                };

                return result;
            }
            catch (Exception ex)
            {
                return new AnalysisResult
                {
                    IsSuccessful = false,
                    ErrorMessage = $"Analysis error: {ex.Message}"
                };
            }
        }
    }
}
