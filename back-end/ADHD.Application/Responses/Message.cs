using System.Collections.Generic;

namespace ADHD.Application.Responses
{
    public record Message(IEnumerable<string> To, string Subject, string Body);
}
