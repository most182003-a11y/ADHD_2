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

        // Simon Memory fields
        public int? FinalLevel { get; set; }
        public int? TotalCorrectSteps { get; set; }
        public int? TotalSteps { get; set; }
        public int? PrematurePressesDuringShow { get; set; }
        public string? EndStatus { get; set; }

        // Reaction Time fields
        public int? Hits { get; set; }
        public int? FalseStarts { get; set; }
        public int? Misses { get; set; }
        public int? ImpulsiveErrors { get; set; }
        public int? WrongButtons { get; set; }
        public double? ReactionTimeStdDevMs { get; set; }
        public double? ImpulsivityScore { get; set; }
        public double? AttentionScore { get; set; }
    }
}
