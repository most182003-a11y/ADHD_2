namespace ADHD.Domain.Entities
{
    public class SessionSummary : BaseEntity
    {
        public string SessionId { get; set; } = string.Empty;
        public GameSession? Session { get; set; }

        public int TotalTrials { get; set; }

        public double? AverageReactionTimeMs { get; set; }
        public double? AverageSimilarity { get; set; }
        public double? TotalFidgetScore { get; set; }
        public double? AttentionOverall { get; set; }

        public double? AverageStopReactionTimeMs { get; set; }
        public int? FalseStartCount { get; set; }
        public double? AverageFreezeQuality { get; set; }
        public double? MovementIntensityOverall { get; set; }
    }
}
