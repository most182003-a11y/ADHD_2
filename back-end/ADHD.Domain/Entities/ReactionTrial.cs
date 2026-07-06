namespace ADHD.Domain.Entities
{
    public class ReactionTrial : BaseEntity
    {
        public string SessionId { get; set; } = string.Empty;
        public GameSession? Session { get; set; }

        public int Trial { get; set; }
        public int TargetLED { get; set; }
        public double Delay { get; set; }
        public string Result { get; set; } = string.Empty;
        public int PressedButton { get; set; }
        public double? ReactionTimeMs { get; set; }
        public bool Correct { get; set; }
        public bool ImpulsiveError { get; set; }
    }
}
