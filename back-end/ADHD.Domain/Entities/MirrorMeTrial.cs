namespace ADHD.Domain.Entities
{
    public class MirrorMeTrial : BaseEntity
    {
        public string SessionId { get; set; } = string.Empty;
        public GameSession? Session { get; set; }

        public int TrialIndex { get; set; }
        public string? TargetPoseId { get; set; }
        public int ReactionTimeMs { get; set; }
        public double PoseSimilarity { get; set; }
        public int HoldingDurationMs { get; set; }
        public double FidgetScore { get; set; }
        public bool PrematureMovement { get; set; }
        public double AttentionPercent { get; set; }
    }
}
