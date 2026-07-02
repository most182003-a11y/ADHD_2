namespace ADHD.Domain.Enums
{
    public enum Gender { Male, Female }

    public enum DiagnosisSeverity { Mild, Moderate, Severe }

    public enum ChildStatus { Improving, Stable, NeedsIntervention }

    public enum DifficultyLevel { Easy, Medium, Hard }

    /// <summary>
    /// Computed after each session by comparing the last N sessions' PlayerScore.
    /// </summary>
    public enum PerformanceTrend { Improving, Stable, Declining, Insufficient }
}
