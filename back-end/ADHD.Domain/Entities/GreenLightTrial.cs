namespace ADHD.Domain.Entities
{
    public class GreenLightTrial : BaseEntity
    {
        public string SessionId { get; set; } = string.Empty;
        public GameSession? Session { get; set; }

        public int TrialIndex { get; set; }
        public string Phase { get; set; } = string.Empty;
        public int? StopSignalDelayMs { get; set; }
        public double? MovementIntensity { get; set; }
        public int? StopReactionTimeMs { get; set; }
        public double? FreezeQuality { get; set; }
        public bool? FalseStart { get; set; }
    }
}
