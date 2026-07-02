using System.Collections.Generic;

namespace ADHD.Domain.Entities
{
    public class Parent : AppUser
    {
        public ICollection<Child> Children { get; set; } = new List<Child>();
    }
}
