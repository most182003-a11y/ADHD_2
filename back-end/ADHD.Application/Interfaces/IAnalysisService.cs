using System.Threading.Tasks;

namespace ADHD.Application.Interfaces
{
    public class AnalysisResult
    {
        public double? AttentionScore { get; set; }
        public double? ImpulsivityScore { get; set; }
        public double? MotorControlScore { get; set; }

        public string? AttentionChange { get; set; }
        public string? ImpulsivityChange { get; set; }
        public string? MotorControlChange { get; set; }

        public string? SummaryText { get; set; }
        public string[]? Recommendations { get; set; }

        public bool IsSuccessful { get; set; }
        public string? ErrorMessage { get; set; }
        public string? RawRequestJson { get; set; }
        public string? RawResponseJson { get; set; }
        public string? ModelUsed { get; set; }
    }

    public interface IAnalysisService
    {
        Task<AnalysisResult> AnalyzeSessionAsync(string childId, string sessionId, int previousSessionsCount, object sessionData, object[]? trials, object summary);
    }
}
