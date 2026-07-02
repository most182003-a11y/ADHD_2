using ADHD.Application.Responses;
using MediatR;

namespace ADHD.Application.Commands.AdminCommands
{
    public class CreateAdminCommand : IRequest<Response<string>>
    {
        public string Name { get; set; } = string.Empty;
        public string Email { get; set; } = string.Empty;
    }
}
