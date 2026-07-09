using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using ADHD.Application.Interfaces;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace ADHD.Infrastructure.Services
{
    public class HuggingFaceAnalysisService : IAnalysisService
    {
        private readonly HttpClient _httpClient;
        private readonly string _apiToken;
        private readonly string _model;
        private readonly string _apiUrl;
        private readonly ILogger<HuggingFaceAnalysisService> _logger;

        public HuggingFaceAnalysisService(HttpClient httpClient, IConfiguration configuration, ILogger<HuggingFaceAnalysisService> logger)
        {
            _httpClient = httpClient;
            _logger = logger;

            _apiToken = Environment.GetEnvironmentVariable("HF_API_TOKEN")
                        ?? configuration["HuggingFace:ApiToken"]
                        ?? string.Empty;

            _model = configuration["HuggingFace:Model"] ?? "lol";

            var baseUrl = configuration["HuggingFace:ApiUrl"]
                          ?? "https://router.huggingface.co/v1";

            if (baseUrl.Contains("/v1"))
            {
                _apiUrl = $"{baseUrl.TrimEnd('/')}/chat/completions";
            }
            else
            {
                _apiUrl = $"{baseUrl.TrimEnd('/')}/{_model}";
            }

            if (!_httpClient.DefaultRequestHeaders.Contains("User-Agent"))
            {
                _httpClient.DefaultRequestHeaders.Add("User-Agent", 
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36");
            }
        }

        public async Task<AnalysisResult> AnalyzeSessionAsync(
            string childId, string sessionId, int previousSessionsCount,
            object sessionData, object[]? trials, object summary)
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

            bool isPlaceholderToken = string.IsNullOrEmpty(_apiToken) ||
                                      _apiToken.Equals("YOUR_HUGGING_FACE_API_TOKEN_HERE", StringComparison.OrdinalIgnoreCase);

            if (isPlaceholderToken)
            {
                _logger.LogWarning("Missing or placeholder Hugging Face API Token. Cannot perform AI analysis.");
                return new AnalysisResult
                {
                    IsSuccessful = false,
                    ErrorMessage = "Missing or placeholder Hugging Face API Token",
                    RawRequestJson = rawRequestJson,
                    ModelUsed = _model
                };
            }

            try
            {
                var systemPrompt = @"You are an ADHD child performance analyst. Analyze the child's session data and return ONLY valid JSON matching this schema (do NOT include markdown like ```json or any extra text):
{
  ""scores"": {
    ""attention"": 0-100,
    ""impulsivity"": 0-100,
    ""motorControl"": 0-100
  },
  ""trend"": {
    ""attentionChange"": ""+X%"" or ""-X%"",
    ""impulsivityChange"": ""+X%"" or ""-X%"",
    ""motorControlChange"": ""+X%"" or ""-X%""
  },
  ""summaryText"": ""Arabic summary of the child's performance (accurate and matching the calculated scores)"",
  ""recommendations"": [""Arabic recommendation 1"", ""Arabic recommendation 2""]
}

Guidelines for Score Calculation:
1. Scale Interpretation:
   - AttentionOverall, AttentionPercent, PoseSimilarity, and AverageSimilarity are decimal fractions between 0.0 and 1.0 (where 1.0 is 100%).
   - You MUST multiply these by 100 to map them to the 0-100 scale! (e.g., 1 or 1.0 = 100, 0.97 = 97, 0.85 = 85).
2. Attention Score (0-100, higher is better):
   - Map from AttentionOverall (or the average of AttentionPercent in trials). If AttentionOverall is 1.0, the attention score is 100.
3. Impulsivity Score (0-100, lower is better):
   - Calculate based on PrematureMovement boolean values in trials, and FalseStartCount / FalseStarts in sessionSummary.
   - PrematureMovement = true means the child moved before/during the pose prompt (which is impulsive).
   - If the child has PrematureMovement = true in all or most trials (e.g., 5 out of 5), their impulsivity score is very high (e.g., 80-100).
   - If PrematureMovement is false in all trials and there are no false starts, the impulsivity score is very low (e.g., 0-15).
4. Motor Control Score (0-100, higher is better):
   - Calculate based on PoseSimilarity / AverageSimilarity (multiply by 100) and FidgetScore / TotalFidgetScore.
   - High similarity (0.90+) and zero fidgeting = high motor control (e.g., 85-100).
   - Higher fidgeting or lower similarity reduces the score.
5. Consistency Rules:
   - Your Arabic summaryText and recommendations MUST be consistent with the calculated scores.
   - Do NOT say the child has 1% focus if their AttentionOverall is 1.0 (100%). Use the converted percentage (100%).
   - If impulsivity is high (e.g., 100), do NOT say 'لم يتم تسجيل أي حركات مبكرة' (no early movements were recorded) when PrematureMovement is true in the data. Be accurate.
   - All trend values compare to previous sessions. If previousSessionsCount is 0, all trend changes must be '+0%' or '-0%'.";

                var prompt = $"{systemPrompt}\n\nSession Data:\n{rawRequestJson}\n\nResponse:";

                object requestBody;
                if (_apiUrl.Contains("/chat/completions"))
                {
                    requestBody = new
                    {
                        model = _model,
                        messages = new[]
                        {
                            new { role = "system", content = "You are a helpful assistant that only returns raw JSON matching the requested schema. Do not output any markdown formatting like ```json or ```." },
                            new { role = "user", content = prompt }
                        },
                        max_tokens = 1500,
                        temperature = 0.2
                    };
                }
                else
                {
                    requestBody = new
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
                }

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
                    _logger.LogWarning("Hugging Face API returned non-success status code {StatusCode}.", response.StatusCode);
                    return new AnalysisResult
                    {
                        IsSuccessful = false,
                        ErrorMessage = $"HF API Error: {response.StatusCode} - {responseBody}",
                        RawRequestJson = rawRequestJson,
                        RawResponseJson = responseBody,
                        ModelUsed = _model
                    };
                }

                var rawResponseJson = responseBody;

                string content = string.Empty;
                using (var jsonDoc = JsonDocument.Parse(responseBody))
                {
                    var root = jsonDoc.RootElement;
                    if (root.TryGetProperty("choices", out var choices) && choices.ValueKind == JsonValueKind.Array && choices.GetArrayLength() > 0)
                    {
                        var message = choices[0].GetProperty("message");
                        content = message.GetProperty("content").GetString() ?? string.Empty;
                    }
                    else if (root.TryGetProperty("generated_text", out var genText))
                    {
                        content = genText.GetString() ?? string.Empty;
                    }
                    else if (root.ValueKind == JsonValueKind.Array && root.GetArrayLength() > 0)
                    {
                        content = root[0].GetProperty("generated_text").GetString() ?? string.Empty;
                    }
                    else
                    {
                        content = responseBody;
                    }
                }

                if (string.IsNullOrEmpty(content))
                {
                    _logger.LogWarning("Empty response from Hugging Face.");
                    return new AnalysisResult
                    {
                        IsSuccessful = false,
                        ErrorMessage = "Empty response content from Hugging Face model",
                        RawRequestJson = rawRequestJson,
                        RawResponseJson = responseBody,
                        ModelUsed = _model
                    };
                }

                content = ExtractJson(content);

                if (string.IsNullOrEmpty(content))
                {
                    _logger.LogWarning("Could not extract JSON from HF response.");
                    return new AnalysisResult
                    {
                        IsSuccessful = false,
                        ErrorMessage = "Could not extract JSON from model response text. Raw content: " + content,
                        RawRequestJson = rawRequestJson,
                        RawResponseJson = responseBody,
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
                _logger.LogError(ex, "Exception during Hugging Face analysis execution.");
                return new AnalysisResult
                {
                    IsSuccessful = false,
                    ErrorMessage = $"Exception: {ex.Message} - {ex.StackTrace}",
                    RawRequestJson = rawRequestJson,
                    ModelUsed = _model
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
