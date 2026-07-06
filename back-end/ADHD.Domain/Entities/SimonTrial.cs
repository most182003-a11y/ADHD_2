namespace ADHD.Domain.Entities
{
    public class SimonTrial : BaseEntity
    {
        public string SessionId { get; set; } = string.Empty;
        public GameSession? Session { get; set; }

        public int Level { get; set; }
        public int SequenceLength { get; set; }
        public double Speed { get; set; }
        public int Step { get; set; }
        public int Expected { get; set; }
        public int Pressed { get; set; }
        public bool Correct { get; set; }
        public double ReactionTimeMs { get; set; }
    }
}
