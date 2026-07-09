using System;

namespace ADHD.Domain.Entities
{
    /// <summary>
    /// Stores AI-processed analysis results for a game session.
    /// This is the "processed data" produced by the AI agent,
    /// separate from the raw metrics stored in SessionSummary.
    /// </summary>
    public class AIAnalysis : BaseEntity
    {
        public string SessionId { get; set; } = string.Empty;
        public GameSession? Session { get; set; }

        // Normalized scores (0-100)
        public double AttentionScore { get; set; }
        public double ImpulsivityScore { get; set; }
        public double MotorControlScore { get; set; }

        // Trend comparison vs previous sessions
        public string? AttentionChange { get; set; }
        public string? ImpulsivityChange { get; set; }
        public string? MotorControlChange { get; set; }

        // AI-generated content (Arabic)
        public string? SummaryText { get; set; }
        public string? RecommendationsJson { get; set; }

        // Metadata for debugging and auditing
        public string? ModelUsed { get; set; }
        public string? RawRequestJson { get; set; }
        public string? RawResponseJson { get; set; }
        public bool IsSuccessful { get; set; }
        public string? ErrorMessage { get; set; }
        public DateTime AnalysisDate { get; set; } = DateTime.UtcNow;
    }
}
