using ADHD.Domain.Enums;
using System;
using System.Collections.Generic;

namespace ADHD.Domain.Entities
{
    public class Child : BaseEntity
    {
        public string Name { get; set; } = string.Empty;
        public int Age { get; set; }
        public Gender Gender { get; set; }
        public DiagnosisSeverity DiagnosisSeverity { get; set; }
        public DateTime RegisteredDate { get; set; } = DateTime.UtcNow;
        public ChildStatus Status { get; set; } = ChildStatus.Stable;
        public string AvatarInitials { get; set; } = string.Empty;

        public string? DoctorId { get; set; }
        public Doctor? Doctor { get; set; }
        public string? ParentId { get; set; }
        public Parent? Parent { get; set; }

        public ICollection<GameSession> GameSessions { get; set; } = new List<GameSession>();
    }
}
