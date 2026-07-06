using System.Collections.Generic;

namespace ADHD.Domain.Entities
{
    public class GameSession : BaseEntity
    {
        public string ChildId { get; set; } = string.Empty;
        public Child? Child { get; set; }

        public string GameType { get; set; } = string.Empty;
        public int? SessionNumber { get; set; }

        public ICollection<MirrorMeTrial> MirrorMeTrials { get; set; } = new List<MirrorMeTrial>();
        public ICollection<GreenLightTrial> GreenLightTrials { get; set; } = new List<GreenLightTrial>();
        public ICollection<SimonTrial> SimonTrials { get; set; } = new List<SimonTrial>();
        public ICollection<ReactionTrial> ReactionTrials { get; set; } = new List<ReactionTrial>();
        public SessionSummary? Summary { get; set; }
    }
}
