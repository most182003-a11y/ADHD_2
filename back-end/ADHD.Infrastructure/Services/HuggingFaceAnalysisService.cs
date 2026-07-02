using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using ADHD.Application.Interfaces;
using Microsoft.Extensions.Configuration;

namespace ADHD.Infrastructure.Services
{
    public class HuggingFaceAnalysisService : IAnalysisService
    {
        private readonly HttpClient _httpClient;
        private readonly string _apiToken;
        private readonly string _model;
        private readonly string _apiUrl;

        public HuggingFaceAnalysisService(HttpClient httpClient, IConfiguration configuration)
        {
            _httpClient = httpClient;

            _apiToken = Environment.GetEnvironmentVariable("HF_API_TOKEN")
                        ?? configuration["HuggingFace:ApiToken"]
                        ?? string.Empty;

            _model = configuration["HuggingFace:Model"] ?? "mistralai/Mistral-7B-Instruct-v0.3";

            var baseUrl = configuration["HuggingFace:ApiUrl"]
                          ?? "https://api-inference.huggingface.co/models";

            _apiUrl = $"{baseUrl}/{_model}";
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

                var systemPrompt = @"You are an ADHD child performance analyst. Analyze the following session data and return ONLY valid JSON (no markdown, no extra text):

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
  ""summaryText"": ""Arabic summary of child's performance"",
  ""recommendations"": [""rec1"", ""rec2"", ""rec3""]
}

Rules:
- attention: higher is better
- impulsivity: lower is better  
- motorControl: higher is better
- trend compares to previous sessions (0% if no previous sessions)
- summaryText in Arabic
- 2-4 recommendations based on performance";

                var prompt = $"{systemPrompt}\n\nSession Data:\n{rawRequestJson}\n\nResponse:";

                var requestBody = new
                {
                    inputs = prompt,
                    parameters = new
                    {
                        temperature = 0.3,
                        max_new_tokens = 2000,
                        return_full_text = false,
                        stop = new[] { "}" }
                    }
                };

                var httpContent = new StringContent(
                    JsonSerializer.Serialize(requestBody),
                    Encoding.UTF8,
                    "application/json");

                if (!string.IsNullOrEmpty(_apiToken))
                {
                    _httpClient.DefaultRequestHeaders.Remove("Authorization");
                    _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {_apiToken}");
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

                string content;
                using (var jsonDoc = JsonDocument.Parse(responseBody))
                {
                    var root = jsonDoc.RootElement;
                    if (root.ValueKind == JsonValueKind.Array)
                    {
                        content = root[0].GetProperty("generated_text").GetString() ?? string.Empty;
                    }
                    else if (root.TryGetProperty("generated_text", out var genText))
                    {
                        content = genText.GetString() ?? string.Empty;
                    }
                    else
                    {
                        content = responseBody;
                    }
                }

                if (string.IsNullOrEmpty(content))
                {
                    return new AnalysisResult
                    {
                        IsSuccessful = false,
                        ErrorMessage = "Empty response from Hugging Face",
                        RawRequestJson = rawRequestJson,
                        RawResponseJson = rawResponseJson,
                        ModelUsed = _model
                    };
                }

                content = ExtractJson(content);

                if (string.IsNullOrEmpty(content))
                {
                    return new AnalysisResult
                    {
                        IsSuccessful = false,
                        ErrorMessage = "Could not extract JSON from model response",
                        RawRequestJson = rawRequestJson,
                        RawResponseJson = rawResponseJson,
                        ModelUsed = _model
                    };
                }

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

        private static string ExtractJson(string text)
        {
            var start = text.IndexOf('{');
            if (start < 0) return string.Empty;

            var depth = 0;
            var end = -1;
            for (var i = start; i < text.Length; i++)
            {
                if (text[i] == '{') depth++;
                else if (text[i] == '}') depth--;
                if (depth == 0)
                {
                    end = i;
                    break;
                }
            }

            return end > start ? text.Substring(start, end - start + 1) : string.Empty;
        }
    }
}
