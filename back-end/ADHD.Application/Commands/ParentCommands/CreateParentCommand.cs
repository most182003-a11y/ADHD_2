using ADHD.Application.Responses;
using MediatR;

namespace ADHD.Application.Commands.ParentCommands
{
    public class CreateParentCommand : IRequest<Response<string>>
    {
        public string Name { get; set; } = string.Empty;
        public string Email { get; set; } = string.Empty;
        public string? PhoneNumber { get; set; }
    }
}
