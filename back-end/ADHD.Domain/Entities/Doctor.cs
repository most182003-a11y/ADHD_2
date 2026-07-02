using System.Collections.Generic;

namespace ADHD.Domain.Entities
{
    public class Doctor : AppUser
    {
        public string? Specialization { get; set; }
        public ICollection<Child> Patients { get; set; } = new List<Child>();
    }
}
